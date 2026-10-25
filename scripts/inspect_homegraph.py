"""Fetch a raw Google Home graph and show which of its fields `api.proto` maps.

`fetch` saves the raw `GetHomeGraph` response to a file only you can read. The
file holds local auth tokens and other account data, so never share it.

`summary` decodes that file without the schema and prints every field of every
message, with redacted samples, and marks fields that `api.proto` does not map
or maps with the wrong type.

    uv run --with 'glocaltokens>=1.0.0' scripts/inspect_homegraph.py fetch ~/homegraph.bin
    uv run scripts/inspect_homegraph.py summary ~/homegraph.bin

`fetch` reads the master token from `GOOGLE_MASTER_TOKEN` or asks for it.
"""

import argparse
from collections import Counter
from dataclasses import dataclass, field
import getpass
import os
from pathlib import Path
import re
import struct

from google.protobuf.descriptor import Descriptor, FieldDescriptor

from ghome_foyer_api.api_pb2 import GetHomeGraphRequest, GetHomeGraphResponse

GET_HOME_GRAPH = "/google.internal.home.foyer.v1.StructuresService/GetHomeGraph"
MAX_FIELD_NUMBER = 2**29 - 1
VARINT, FIXED64, LENGTH_DELIMITED, FIXED32 = 0, 1, 2, 5

# Shown only as their length, with every field inside them, mapped or not
SENSITIVE_FIELDS = {
    "address",
    "duo_call_url",
    "duo_phone_number",
    "email_address",
    "latitude",
    "local_auth_token",
    "location",
    "longitude",
}
UUID = re.compile(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}", re.IGNORECASE)
URL = re.compile(r"(\w+://[^/\s]*)\S*")
EMAIL = re.compile(r"\S+@\S+")
# Tokens and keys: long runs of token characters with both letters and digits.
# Dotted names such as action.devices.traits.OnOff have no digits and stay.
TOKEN = re.compile(r"[\w+/=.:~-]{20,}", re.ASCII)
DIGITS = re.compile(r"\+?\d[\d\s().-]{5,}\d")

WIRE_TYPES = {VARINT: "varint", FIXED64: "fixed64", FIXED32: "fixed32"}
DECLARED_WIRE_TYPE = {
    FieldDescriptor.TYPE_DOUBLE: FIXED64,
    FieldDescriptor.TYPE_FIXED64: FIXED64,
    FieldDescriptor.TYPE_SFIXED64: FIXED64,
    FieldDescriptor.TYPE_FLOAT: FIXED32,
    FieldDescriptor.TYPE_FIXED32: FIXED32,
    FieldDescriptor.TYPE_SFIXED32: FIXED32,
    FieldDescriptor.TYPE_STRING: LENGTH_DELIMITED,
    FieldDescriptor.TYPE_BYTES: LENGTH_DELIMITED,
    FieldDescriptor.TYPE_MESSAGE: LENGTH_DELIMITED,
}
TYPE_NAMES = {
    getattr(FieldDescriptor, name): name.removeprefix("TYPE_").lower()
    for name in dir(FieldDescriptor)
    if name.startswith("TYPE_")
}


@dataclass
class WireField:
    number: int
    wire_type: int
    value: int | bytes


@dataclass
class FieldStats:
    declared: FieldDescriptor | None
    kinds: Counter[str] = field(default_factory=Counter)
    samples: Counter[str] = field(default_factory=Counter)
    present: int = 0
    max_per_message: int = 0


@dataclass
class MessageStats:
    descriptor: Descriptor | None
    count: int = 0
    fields: dict[int, FieldStats] = field(default_factory=dict)


def read_varint(data: bytes, pos: int) -> tuple[int, int]:
    """Return the varint at `pos` and the position after it."""
    result = shift = 0
    while pos < len(data) and shift < 64:
        byte = data[pos]
        pos += 1
        result |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return result, pos
        shift += 7
    raise ValueError("truncated varint")


def parse_message(data: bytes) -> list[WireField]:
    """Split `data` into wire fields, or raise ValueError if it is not a message."""
    fields = []
    pos = 0
    while pos < len(data):
        key, pos = read_varint(data, pos)
        number, wire_type = key >> 3, key & 7
        if not 0 < number <= MAX_FIELD_NUMBER:
            raise ValueError("bad field number")
        value: int | bytes
        if wire_type == VARINT:
            value, pos = read_varint(data, pos)
        elif wire_type in (FIXED64, FIXED32):
            size = 8 if wire_type == FIXED64 else 4
            value, pos = data[pos : pos + size], pos + size
        elif wire_type == LENGTH_DELIMITED:
            size, pos = read_varint(data, pos)
            value, pos = data[pos : pos + size], pos + size
        else:
            raise ValueError("groups are not supported")
        if pos > len(data):
            raise ValueError("truncated field")
        fields.append(WireField(number, wire_type, value))
    return fields


def redact(text: str, secret: bool, address: re.Pattern[str] | None) -> str:
    """Return `text` with address parts, tokens, emails, URLs and long numbers masked."""
    if secret:
        return f"<redacted len={len(text)}>"
    if address:
        text = address.sub("<address>", text)
    text = UUID.sub("<uuid>", text)
    text = URL.sub(r"\1/<redacted>", text)
    text = EMAIL.sub("<email>", text)
    text = TOKEN.sub(
        lambda m: (
            f"<token len={len(m[0])}>"
            if re.search(r"\d", m[0]) and re.search(r"[A-Za-z]", m[0])
            else m[0]
        ),
        text,
    )
    text = DIGITS.sub(lambda m: f"<digits len={len(m[0])}>", text)
    return repr(text if len(text) <= 60 else text[:57] + "...")


def describe(
    wire: WireField,
    declared: FieldDescriptor | None,
    secret: bool,
    address: re.Pattern[str] | None,
) -> tuple[str, str | None, list[WireField] | None]:
    """Return the field's kind, a redacted sample and its subfields, if any."""
    if isinstance(wire.value, int):
        return "varint", "<redacted>" if secret else str(wire.value), None
    if wire.wire_type in (FIXED64, FIXED32):
        fmt = "<d" if wire.wire_type == FIXED64 else "<f"
        value = float(struct.unpack(fmt, wire.value)[0])
        # Coordinates turn up in unmapped fields too, so show only whole numbers
        if secret or not value.is_integer():
            return WIRE_TYPES[wire.wire_type], "<fraction>", None
        return WIRE_TYPES[wire.wire_type], f"{value:.0f}", None
    data = wire.value
    if not data:
        return "empty", None, None
    try:
        text = data.decode()
    except UnicodeDecodeError:
        text = None
    # Text is printable; a message starts with a control byte such as \n
    is_text = text is not None and text.isprintable()
    declared_message = declared is not None and declared.message_type is not None
    if is_text and not declared_message:
        return "string", redact(data.decode(), secret, address), None
    try:
        return "message", None, parse_message(data)
    except ValueError:
        if declared and declared.type == FieldDescriptor.TYPE_STRING:
            text = data.decode(errors="replace")
            return "string", redact(text, secret, address), None
        return "bytes", f"<bytes len={len(data)}>", None


def collect(
    fields: list[WireField],
    path: str,
    descriptor: Descriptor | None,
    stats: dict[str, MessageStats],
    secret: bool,
    address: re.Pattern[str] | None,
) -> None:
    """Add one message's fields to `stats`, recursing into submessages.

    `secret` hides every value in the message, as its parent is sensitive.
    """
    message = stats.setdefault(path, MessageStats(descriptor))
    message.count += 1
    for number, count in Counter(wire.number for wire in fields).items():
        declared = descriptor.fields_by_number.get(number) if descriptor else None
        field_stats = message.fields.setdefault(number, FieldStats(declared))
        field_stats.present += 1
        field_stats.max_per_message = max(field_stats.max_per_message, count)
    for wire in fields:
        field_stats = message.fields[wire.number]
        declared = field_stats.declared
        field_secret = secret or (
            declared is not None and declared.name in SENSITIVE_FIELDS
        )
        kind, sample, subfields = describe(wire, declared, field_secret, address)
        field_stats.kinds[kind] += 1
        if sample is not None:
            field_stats.samples[sample] += 1
        if subfields is not None:
            name = declared.name if declared else f"#{wire.number}"
            child = declared.message_type if declared else None
            collect(subfields, f"{path}.{name}", child, stats, field_secret, address)


def problems(field_stats: FieldStats) -> list[str]:
    """Return how `api.proto` disagrees with what the field holds."""
    declared = field_stats.declared
    if declared is None:
        return ["UNMAPPED"]
    found = []
    expected = DECLARED_WIRE_TYPE.get(declared.type, VARINT)
    kinds = set(field_stats.kinds) - {"empty"}
    actual = {
        {"varint": VARINT, "fixed64": FIXED64, "fixed32": FIXED32}.get(kind, 2)
        for kind in kinds
    }
    repeated = declared.is_repeated
    if repeated and expected != LENGTH_DELIMITED:
        actual.discard(LENGTH_DELIMITED)  # packed repeated numbers
    if actual - {expected}:
        found.append(f"WIRE TYPE: declared {TYPE_NAMES[declared.type]}")
    if declared.type == FieldDescriptor.TYPE_STRING and "message" in kinds:
        found.append("MESSAGE? declared string")
    if field_stats.max_per_message > 1 and not repeated:
        found.append("REPEATED: declared singular")
    return found


def summarise(raw: bytes) -> str:
    """Return a redacted field map of a raw GetHomeGraph response."""
    # Parts of the home's address, such as the town, also turn up in other fields
    home_address = GetHomeGraphResponse.FromString(raw).home.location.address
    parts = {part.strip() for part in home_address.split(",")}
    parts |= {word for part in parts for word in part.split()}
    parts = {part for part in parts if len(part) >= 3}
    address = (
        re.compile(
            "|".join(re.escape(part) for part in sorted(parts, key=len, reverse=True)),
            re.IGNORECASE,
        )
        if parts
        else None
    )
    stats: dict[str, MessageStats] = {}
    collect(
        parse_message(raw),
        "response",
        GetHomeGraphResponse.DESCRIPTOR,
        stats,
        secret=False,
        address=address,
    )
    lines = []
    flagged = 0
    for path, message in stats.items():
        type_name = message.descriptor.name if message.descriptor else "UNMAPPED"
        lines.append(f"\n{path}  [{type_name}]  x{message.count}")
        for number, field_stats in sorted(message.fields.items()):
            declared = field_stats.declared
            name = declared.name if declared else "?"
            kinds = "/".join(sorted(field_stats.kinds))
            seen = f"{field_stats.present}/{message.count}"
            if field_stats.max_per_message > 1:
                seen += f" up to {field_stats.max_per_message}"
            top = [sample for sample, _ in field_stats.samples.most_common(4)]
            if len(field_stats.samples) > len(top):
                top.append(f"({len(field_stats.samples)} distinct)")
            found = problems(field_stats)
            flagged += bool(found)
            flags = f"  !! {', '.join(found)}" if found else ""
            lines.append(
                f"  {number:>4} {name:<24} {kinds:<14} {seen:<14} {', '.join(top)}{flags}"
            )
        if message.descriptor:
            missing = [
                f"{f.number} {f.name}"
                for f in message.descriptor.fields
                if f.number not in message.fields
            ]
            if missing:
                lines.append(f"       not present: {', '.join(missing)}")
    lines.insert(0, f"{len(raw)} bytes, {flagged} fields flagged")
    return "\n".join(lines)


def fetch(output: Path) -> None:
    """Save the raw GetHomeGraph response to `output`, readable only by you."""
    # Only fetch needs these: summary runs without glocaltokens installed
    import grpc  # noqa: PLC0415
    from glocaltokens.client import GLocalAuthenticationTokens  # noqa: PLC0415
    from glocaltokens.const import (  # noqa: PLC0415
        GOOGLE_HOME_FOYER_API,
        REQUEST_TIMEOUT,
    )

    master_token = os.environ.get("GOOGLE_MASTER_TOKEN") or getpass.getpass(
        "Master token: "
    )
    client = GLocalAuthenticationTokens(master_token=master_token)
    credentials = grpc.composite_channel_credentials(
        grpc.ssl_channel_credentials(),
        grpc.access_token_call_credentials(client.get_access_token()),
    )
    with grpc.secure_channel(GOOGLE_HOME_FOYER_API, credentials) as channel:
        # Without a deserializer the call returns the raw bytes, which keep
        # the fields api.proto does not map
        call = channel.unary_unary(
            GET_HOME_GRAPH, request_serializer=None, response_deserializer=None
        )
        raw = call(GetHomeGraphRequest().SerializeToString(), timeout=REQUEST_TIMEOUT)
    fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    os.fchmod(fd, 0o600)
    with os.fdopen(fd, "wb") as file:
        file.write(raw)
    print(
        f"Saved {len(raw)} bytes to {output}. It holds local auth tokens: keep it private."
    )


def selftest() -> None:
    """Check that summary output leaks none of the secrets in a fake home graph."""

    def varint(value: int) -> bytes:
        out = b""
        while value > 0x7F:
            out += bytes([value & 0x7F | 0x80])
            value >>= 7
        return out + bytes([value])

    def key(number: int, wire_type: int) -> bytes:
        return varint(number << 3 | wire_type)

    local_auth_token = "Ab3" * 36
    access_token = "ya29.a0AfH6SMBx1234567890abcdefXYZ"
    response = GetHomeGraphResponse()
    home = response.home
    home.home_name = "Test home"
    home.location.address = "1 Secret Street, Hiddenville"
    home.location.coordinates.latitude = 51.123456
    home.location.timezone = "Europe/Hiddenville"
    # Unmapped fields inside the location are hidden too
    home.location.MergeFromString(key(9, VARINT) + varint(987654))
    home.linked_users.add().email_address = "someone@example.com"
    device = home.devices.add()
    device.device_name = "Kitchen speaker"
    device.local_auth_token = local_auth_token
    device.device_type = "action.devices.types.SPEAKER"
    raw = (
        response.SerializeToString()
        + key(98, VARINT)
        + b"\x07"
        + key(95, FIXED64)
        + struct.pack("<d", -0.123456)
    )
    for number, text in (
        (99, f"call https://example.com/x?key={access_token} or +44 20 7946 0958"),
        (97, f"Bearer {access_token}"),
        (96, "Weather for Hiddenville"),
    ):
        raw += key(number, LENGTH_DELIMITED) + bytes([len(text)]) + text.encode()
    out = summarise(raw)
    for secret in (
        local_auth_token[:12],
        access_token[:12],
        "Secret Street",
        "Hiddenville",
        "987654",
        "51.12",
        "0.12",
        "someone",
        "7946",
    ):
        assert secret not in out, secret
    for expected in (
        "'Kitchen speaker'",
        "action.devices.types.SPEAKER",
        "'Weather for <address>'",
        "UNMAPPED",
    ):
        assert expected in out, expected
    print("ok")


def main() -> None:
    """Run the command given on the command line."""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("fetch").add_argument("output", type=Path)
    commands.add_parser("summary").add_argument("input", type=Path)
    commands.add_parser("selftest")
    args = parser.parse_args()
    if args.command == "fetch":
        fetch(args.output)
    elif args.command == "summary":
        print(summarise(args.input.read_bytes()))
    else:
        selftest()


if __name__ == "__main__":
    main()
