[![CI](https://github.com/KapJI/ghome-foyer-api/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/KapJI/ghome-foyer-api/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/ghome-foyer-api)](https://pypi.org/project/ghome-foyer-api/)

# Google Home Foyer API

With this package, multiple libraries can use Foyer API without having to deal with Protobuf version conflicts.

- Only one version of stubs can be loaded by Protobuf at the same time even if stubs are coming from different libraries and modules have different names. Using this package ensures that only one version is installed at any given time.
- The package defines dependencies on Protobuf and GRPC, ensuring compatibility of generated files.
- Type hints are generated and exported as well.

Files can be regenerated using `scripts/generate.sh`.

## Credits

The proto file is taken from [here](https://github.com/rithvikvibhu/GHLocalApi/issues/39).
Thanks [@rithvikvibhu](https://github.com/rithvikvibhu) for extracting it.
