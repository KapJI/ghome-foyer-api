# Google Home Foyer API

With this package, multiple libraries can use Foyer API without having to deal with Protobuf version conflicts.

- Only one version of stubs can be loaded by Protobuf at the same time even if stubs are coming from different libraries and modules have different names. Using this package ensures that only one version is installed at any given time.
- The package defines dependencies on Protobuf and GRPC, ensuring compatibility of generated files.
- Type hints are generated and exported as well.

## Credits

The proto file is taken from [here](https://github.com/rithvikvibhu/GHLocalApi/issues/39).
Thanks [@rithvikvibhu](https://github.com/rithvikvibhu) for extracting it.
