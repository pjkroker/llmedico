## LLMedico Command Line Options

**Options marked with an asterisk (*) are mandatory.**

### General Options
#TODO
### Analyze

llmedico analyze --target-class=org.apache.commons.lang3.StringUtils --target-method=isNotEmpty --data-dir=/Users/paul/paul_data/projects_cs/ba_versuch1/llmedico/data/input/project --out-dir=/Users/paul/paul_data/projects_cs/ba_versuch1/llmedico/data/output
oder
llmedico analyze --target-class=org.apache.commons.lang3.StringUtils --target-method=isNotEmpty --source-dir=/Users/paul/paul_data/projects_cs/ba_versuch1/llmedico/data/input/project/src/main/java --class-dir=/Users/paul/paul_data/projects_cs/ba_versuch1/llmedico/data/input/project/target/classes --out-dir=/Users/paul/paul_data/projects_cs/ba_versuch1/llmedico/data/output

#/data/input is mandatory --> change later

| Option             | Description                                                                                                                                                                                                                                                                                        |
|--------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `--target-class` * | Fully-qualified name of the class for which LLMedico has to generate test oracles. _e.g. org.apache.commons.lang3.StringUtils_                                                                                                                                                                     |
| `--targer-method` * | Method of class for which LLMedico has to generate test oracles. _e.g. isNotEmpty_                                                                                                                                                                                                                 |
| `--data-dir` *     | Directory containing all the project files of the system under test (the system that includes the target class). _e.g. /data/input/**project**_ <br/> Expects the following: /data/input/project/src/main/java and /data/input/project/target/classes; if not use --source-dir and --class-dir instead |
| `--source-dir`     | Directory containing all the source files of the system under test (the system that includes the target class).  _e.g. /data/input/project/src/main/java_                                                                                                                                          |
| `--class-dir`      | Directory containing binary files of the system under test (the system that includes the target class). _e.g /data/input/project/target/classes_                                                                                                                                                   |
| `--out-dir` *      | Directory to save every output file.                                                                                                                                                                                                                                                               |
| `--help`, `-h`     | Print the list of available options.                                                                                                                                                                                                                                                               |
| `--debug`          | Enable fine-grained logging.                                                                                                                                                                                                                                                                       |
