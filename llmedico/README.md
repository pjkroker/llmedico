## LLMedico Command Line Options

**Options marked with an asterisk (*) are mandatory.**

### General Options

llmedico analyze --target-class=org.apache.commons.lang3.StringUtils --target-method=isNotEmpty --data-dir=/Users/paul/paul_data/projects_cs/ba_versuch1/llmedico/data --out-dir=/Users/paul/paul_data/projects_cs/ba_versuch1/llmedico/data/output

#/data/input is mandatory --> change later

| Option             | Description                                                                                                                                          |
|--------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|
| `--target-class` * | Fully-qualified name of the class for which LLMedico has to generate test oracles. _e.g. org.apache.commons.lang3.StringUtils_                       |
| `--data-dir` *     | Directory containing source files of the system under test (the system that includes the target class). _e.g. **/data**/input/project/src/main/java_ |
| `--class-dir`      | Directory containing binary files of the system under test (the system that includes the target class). _e.g /data/input/project/target/**classes**_ |
| `--out-dir` *      | Directory to save every output file.                                                                                                                 |
| `--targer-method` * | Method of class for which LLMedico has to generate test oracles. _e.g. isNotEmpty_                                                                   |
| `--help`, `-h`     | Print the list of available options.                                                                                                                 |
| `--debug`          | Enable fine-grained logging.                                                                                                                         |
