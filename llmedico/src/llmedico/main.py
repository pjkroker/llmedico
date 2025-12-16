import json
from pathlib import Path

from pydantic.v1.parse import load_file

from llmedico.java_utils.javapy import JavaParser
from llmedico.java_utils.translator.translator import Translator
from pyjdoctor.pyjdoctor import PyJDoctor
import logging
logger = logging.getLogger(__name__)
from pyrandoop.pyrandoop import PyRandoop
from se_helpers.files.files import save_json_to_file, load_json, save_realy_json_to_file


IMAGE = "pjkroker/toradocu-x86-extractor"
LIMIT_METHODS = 40 # defines the number of methods of the class to be analyzed #TODO change
def start_jdoctor(fq_class_name: str, path_data_dir: Path, path_source_dir, path_class_dir, path_output_dir: Path) -> None:
    pyjdoctor = PyJDoctor("/Users/paul/paul_data/projects_cs/ba_versuch1/pyjdoctor", IMAGE, path_data_dir, path_output_dir)
    pyjdoctor.set_data_dir(path_data_dir)
    if path_data_dir is None:
        pyjdoctor.set_source_dir_r(path_source_dir)
        pyjdoctor.set_class_dir_r(path_class_dir)
    else:
        pass

    pyjdoctor.start_container()
    pyjdoctor.generate_all(fq_class_name)
    pyjdoctor.generate_statistics(fq_class_name, "/input/toradocu-condition_translator.json")
    pyjdoctor.stop_container()

def start_java_parser(path_output_dir: Path, path_java_class: Path):
    jp = JavaParser()
    result_json = jp.extract_to_json(path_java_class)
    save_json_to_file(result_json, path_output_dir / "llmedico-javadoc_extractor.json")
    result_json = json.loads(result_json)
    return result_json

#TODO check if generated assertion contain { or }, gets mistaken as python dict seperator?
def start_translator(result_json):
    trans = Translator()
    results = {}

    for i in range(0, LIMIT_METHODS):
        method_name = result_json[0]["methods"][i]["name"]
        javadoc = result_json[0]["methods"][i]["javadoc"]
        javacode = result_json[0]["methods"][i]["code"]
        java_assertions = trans.translate_javadoc(javacode, "return")
        logger.debug(java_assertions)
        results[method_name] = java_assertions
    logger.debug(results)
    return results

def start_translator_with_specified_method(result_json, target_method:str):
    trans = Translator()
    results = {}
    logger.debug(f"target method is: {target_method}")

    for i in range(0, len(result_json[0]["methods"])):
        method_name = result_json[0]["methods"][i]["name"]
        if method_name == target_method:
            javadoc = result_json[0]["methods"][i]["javadoc"]
            javacode = result_json[0]["methods"][i]["code"]
            java_assertions = trans.translate_javadoc(javadoc, modes={"pre", "return"})
            logger.debug(java_assertions)
            results[method_name] = java_assertions
    logger.debug(results)
    return results

def start_translator_everything(result_json):
    trans = Translator()
    results = {}
    logger.debug("start translator")
    logger.debug("translating every method of the class")
    for i in range(0, len(result_json[0]["methods"])):
        method_name = result_json[0]["methods"][i]["name"]
        logger.debug(f"current method name: {method_name}")
        javadoc = result_json[0]["methods"][i]["javadoc"]
        logger.debug(f"has the following javadoc: {javadoc}")

        #get modes
        modes = []
        for tag in result_json[0]["methods"][i]["tags"]:
            modes.append(tag["tag"])
        if not modes: logger.warning(f"{method_name} contains not tags?")
        logger.debug(f"found modes: {modes}")
        java_assertions = trans.translate_javadoc(javadoc, modes=modes)
        logger.debug(f"the following java assertion have been generated: {java_assertions}")
        results[method_name] = java_assertions
    logger.debug(results)
    return results

def insert_conditions(result_json, results, path_output_dir):
    for i in range(0, len(result_json[0]["methods"])):
        method_name = result_json[0]["methods"][i]["name"]
        for j in range(0, len(result_json[0]["methods"][i]["tags"])):
            if result_json[0]["methods"][i]["tags"][j]["tag"] == "param":
                result_json[0]["methods"][i]["tags"][j]["condition"] = results[method_name]["param"][0]
            elif result_json[0]["methods"][i]["tags"][j]["tag"] == "return":
                result_json[0]["methods"][i]["tags"][j]["condition"] = results[method_name]["return"][0]
            elif result_json[0]["methods"][i]["tags"][j]["tag"] == "throws":
                result_json[0]["methods"][i]["tags"][j]["condition"] = results[method_name]["throws"][0]

    # Convert to pretty JSON string for logging
    json_preview = json.dumps(result_json, indent=2, ensure_ascii=False)
    logger.info("Data before dumping:\n%s", json_preview)
    with open(path_output_dir / "llmedico-condition_translator.json", "w", encoding="utf-8") as f:
        json.dump(result_json, f, indent=2, ensure_ascii=False)






def start_validating(results):
    jp = JavaParser()
    valid = {}
    for method_name in results:
        valid[method_name] = []
        for assertion in results[method_name]:
            if jp.is_valid_java_assert(assertion):
                valid[method_name].append(assertion)
            else:
                logger.debug(f"{assertion} is not a valid java assertion")

    logger.debug(valid)
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
                logger.debug(pre_condition)
                pre_conditions.append(pre_condition)
            one_method["pre"] = pre_conditions
            specs.append(one_method)
        except ValueError:
            logger.warning(f"No entry found for method name '{method_name}'")

    logger.debug(specs)
    save_realy_json_to_file(specs, path_output_dir / "llmedico-specs.json")

def start_randoop(path_data_dir: Path, path_class_dir: Path, path_output_dir: Path, fq_class_name: str) -> None:
    if path_data_dir:
        path_class_dir = path_data_dir / "target" / "classes"
    else:
        pass

    rd = PyRandoop(path_output_dir=path_output_dir,
                   class_dir=path_class_dir,
                   time_limit=60, deterministic=False)
    result = rd.generate_dependencies(
        path_class_file=path_class_dir / fq_class_name.replace(".", "/") / ".class")

    result = rd.generate_error_revealing_tests(fq_class_name=fq_class_name, path_oracles=(path_output_dir / "llmedico-specs.json"))
    logger.debug(result["stdout"])

def main(fq_class_name: str, target_method: str, path_data_dir: Path, path_source_dir:Path, path_class_dir: Path,  path_output_dir: Path):
    relative_path = fq_class_name.replace(".", "/") + ".java"

    if path_data_dir is None:
        pass
    else:
        path_java_class = path_data_dir / "src" / "main" / "java" / relative_path
    # Set up basic configuration for logging
    logging.basicConfig(
        filename=path_output_dir / 'llmedico.log',
        filemode='w',  # overwrite on each run
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        force=True
    )
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logger.debug("---Starting LLMedico---")
    # logger.debug("---Starting JDoctor - Extracting JavaDoc---")
    # start_jdoctor(fq_class_name, path_data_dir, path_source_dir, path_class_dir, path_output_dir)
    #
    logger.debug("---Starting JavaParser - Extracting JavaDoc---")
    result_json = start_java_parser(path_output_dir, path_java_class)

    logger.debug("---Starting Translator - Translating JavaDoc to Assertions---")
    #results = start_translator_with_specified_method(result_json, target_method)
    result = start_translator_everything(result_json)
    insert_conditions(result_json, result, path_output_dir)
    # logger.debug("---Validating Syntax of generated Assertions---")
    # valid = start_validating(results)
    #
    # logger.debug("---Adding valid Assertions to Randoop File???---")
    # start_building_randoop_file(valid, path_output_dir)

    # logger.debug("---Generating Tests with Randoop File---")
    # start_randoop(path_data_dir, path_class_dir, path_output_dir, fq_class_name)
    logger.debug("---Ending LLMedico---")


if __name__ == '__main__':
    FQ_CLASS_NAME = "org.apache.commons.math3.primes.Primes"  # --target-class java class to be analyzed
    TARGET_METHOD = "isPrime"  # --target-method#
    PATH_DATA_DIR = Path(
        "/Users/paul/paul_data/projects_cs/ba_versuch1/pyjdoctor/data/input/commons-math3-3.6.1-src")  # --data-dir

    PATH_SOURCE_DIR = None #--source-dir and #--class-dir if no --data-dir was provided
    PATH_CLASS_DIR = None #TODO change if source and class are NOT in the same directory

    PATH_OUTPUT_DIR = Path(
        "/Users/paul/paul_data/projects_cs/ba_versuch1/llmedico/data/output")  # --out-dir

    main(fq_class_name=FQ_CLASS_NAME,
         target_method=TARGET_METHOD,
         path_data_dir=PATH_DATA_DIR if PATH_DATA_DIR else None,
         path_source_dir=PATH_SOURCE_DIR,
         path_class_dir=PATH_CLASS_DIR,
         path_output_dir=PATH_OUTPUT_DIR,)
