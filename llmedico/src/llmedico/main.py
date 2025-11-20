import json
from pathlib import Path

from llmedico.java_utils.javapy import JavaParser
from llmedico.java_utils.translator.translator import Translator
from pyjdoctor.pyjdoctor import PyJDoctor
import logging

from pyrandoop.pyrandoop import PyRandoop
from se_helpers.files.files import save_json_to_file, load_json, save_realy_json_to_file



# PATH_CLASS_DIR = "" #--class-dir #TODO ignore for now
IMAGE = "pjkroker/toradocu-x86-extractor"
LIMIT_METHODS = 40 # defines the number of methods of the class to be analyzed #TODO change
def start_jdoctor(path_data_dir: Path, path_output_dir: Path, fq_class_name: str) -> None:
    pyjdoctor = PyJDoctor("/Users/paul/paul_data/projects_cs/ba_versuch1/pyjdoctor", IMAGE)
    pyjdoctor.set_data_dir(path_data_dir)
    pyjdoctor.set_output_dir(path_output_dir)

    pyjdoctor.start_container()
    pyjdoctor.generate_all(fq_class_name)
    pyjdoctor.stop_container()

def start_java_parser(path_output_dir: Path, path_java_class: Path):
    jp = JavaParser()
    result_json = jp.extract_to_json(path_java_class)
    save_json_to_file(result_json, path_output_dir / "result.json")
    result_json = json.loads(result_json)
    return result_json

def start_translator(result_json):
    trans = Translator()
    results = {}

    for i in range(0, LIMIT_METHODS):
        method_name = result_json[0]["methods"][i]["name"]
        javadoc = result_json[0]["methods"][i]["javadoc"]
        javacode = result_json[0]["methods"][i]["code"]
        java_assertions = trans.translate_javadoc(javacode)
        logging.debug(java_assertions)
        results[method_name] = java_assertions
    logging.debug(results)
    return results

def start_translator_with_specified_method(result_json, target_method:str):
    trans = Translator()
    results = {}
    print(target_method)

    for i in range(0, LIMIT_METHODS):
        method_name = result_json[0]["methods"][i]["name"]
        if method_name == target_method:
            javadoc = result_json[0]["methods"][i]["javadoc"]
            javacode = result_json[0]["methods"][i]["code"]
            java_assertions = trans.translate_javadoc(javacode)
            logging.debug(java_assertions)
            results[method_name] = java_assertions
    logging.debug(results)
    return results


def start_validating(results):
    jp = JavaParser()
    valid = {}
    for method_name in results:
        valid[method_name] = []
        for assertion in results[method_name]:
            if jp.is_valid_java_assert(assertion):
                valid[method_name].append(assertion)
            else:
                logging.debug(f"{assertion} is not a valid java assertion")

    logging.debug(valid)
    return valid

def start_building_randoop_file(valid, path_output_dir: Path):
    # load jdoctor file, remove everything except the one method
    # overwrite pre, post and throws with generated assertions
    jdoctor = load_json( path_output_dir / "toradocu-randoop_specs.json")
    specs = []
    for method_name in valid:
        try:
            one_method = Translator.copy_entry_by_method(jdoctor, method_name)
            pre_conditions = []
            for assertion in valid[method_name]:
                pre_condition = Translator.assertion_to_json(assertion)
                logging.debug(pre_condition)
                pre_conditions.append(pre_condition)
            one_method["pre"] = pre_conditions
            specs.append(one_method)
        except ValueError:
            logging.warning(f"No entry found for method name '{method_name}'")

    logging.debug(specs)
    save_realy_json_to_file(specs, path_output_dir / "llmedico-specs.json")

def start_randoop(path_output_dir: Path, fq_class_name: str) -> None:
    rd = PyRandoop(path_output_dir=path_output_dir,
                   class_dir="/Users/paul/paul_data/projects_cs/ba_versuch1/llmedico/data/input/repository/target/classes",
                   time_limit=60, deterministic=False)
    result = rd.generate_dependencies(
        path_class_file="/Users/paul/paul_data/projects_cs/ba_versuch1/llmedico/data/input/repository/target/classes/org/apache/commons/lang3/StringUtils.class")

    result = rd.generate_error_revealing_tests(fq_class_name=fq_class_name, path_oracles=(path_output_dir / "llmedico-specs.json"))
    logging.debug(result["stdout"])

def main(fq_class_name: str, target_method: str, path_data_dir: Path, path_output_dir: Path):
    relative_path = fq_class_name.replace(".", "/") + ".java"
    path_java_class = path_data_dir / "input" / "repository" / "src" / "main" / "java" / relative_path
    # Set up basic configuration for logging
    logging.basicConfig(
        filename=path_output_dir / 'log.txt',
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        force=True
    )
    logging.debug("---Starting LLMedico---")
    logging.debug("---Starting JDoctor - Extracting JavaDoc---")
    start_jdoctor(path_data_dir, path_output_dir, fq_class_name)

    logging.debug("---Starting JavaParser - Extracting JavaDoc---")
    result_json = start_java_parser(path_output_dir, path_java_class)

    logging.debug("---Starting Translator - Translating JavaDoc to Assertions---")
    results = start_translator_with_specified_method(result_json, target_method)

    logging.debug("---Validating Syntax of generated Assertions---")
    valid = start_validating(results)

    logging.debug("---Adding valid Assertions to Randoop File???---")
    start_building_randoop_file(valid, path_output_dir)

    logging.debug("---Generating Tests with Randoop File---")
    start_randoop(path_output_dir, fq_class_name)
    logging.debug("---Ending LLMedico---")


if __name__ == '__main__':
    FQ_CLASS_NAME = "org.apache.commons.lang3.StringUtils"  # --target-class java class to be analyzed
    TARGET_METHOD = "isNotEmpty"  # --target-method#
    PATH_DATA_DIR = Path(
        "/Users/paul/paul_data/projects_cs/ba_versuch1/llmedico/data")  # --data-dir #TODO change it so that is just project/src/..
    PATH_OUTPUT_DIR = Path(
        "/Users/paul/paul_data/projects_cs/ba_versuch1/llmedico/data/output")  # --out-dir #TODO copy if different

    main(fq_class_name=FQ_CLASS_NAME,
         target_method=TARGET_METHOD,
         path_data_dir=PATH_DATA_DIR,
         path_output_dir=PATH_OUTPUT_DIR,)
