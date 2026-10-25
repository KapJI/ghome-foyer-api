[![CI](https://github.com/KapJI/ghome-foyer-api/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/KapJI/ghome-foyer-api/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/ghome-foyer-api)](https://pypi.org/project/ghome-foyer-api/)

# Google Home Foyer API

With this package, multiple libraries can use Foyer API without having to deal with Protobuf version conflicts.

- Only one version of stubs can be loaded by Protobuf at the same time even if stubs are coming from different libraries and modules have different names. Using this package ensures that only one version is installed at any given time.
- The package defines dependencies on Protobuf and GRPC, ensuring compatibility of generated files.
- Type hints are generated and exported as well.

Files can be regenerated using `scripts/generate.sh`.

## Mapping more fields

`api.proto` maps only part of what Google returns. To see which fields of your own home graph it does not map yet:

```sh
uv run --with 'glocaltokens>=1.0.0' scripts/inspect_homegraph.py fetch ~/homegraph.bin
uv run scripts/inspect_homegraph.py summary ~/homegraph.bin
```

`fetch` asks for your Google master token, or reads it from `GOOGLE_MASTER_TOKEN`, and saves the raw `GetHomeGraph` response to a file only you can read. The file holds the local auth tokens of your devices: keep it outside the repository and never share it.

`summary` lists every field of every message with sample values, and marks fields that `api.proto` does not map (`UNMAPPED`) or declares with the wrong type. It shows only the length of local auth tokens, email addresses and your home's address and coordinates, and masks token-like strings, UUIDs, URL paths and long digit runs wherever they appear. Device, room and home names and other short text stay visible. The masking matches patterns, so read the summary before you share it.

## Credits

The proto file is taken from [here](https://github.com/rithvikvibhu/GHLocalApi/issues/39).
Thanks [@rithvikvibhu](https://github.com/rithvikvibhu) for extracting it.
