import json
from pathlib import Path

from llmedico.java_utils.javapy import JavaParser
from llmedico.java_utils.translator.translator import Translator
from pyjdoctor.pyjdoctor import PyJDoctor
import logging

from pyrandoop.pyrandoop import PyRandoop
from se_helpers.files.files import save_json_to_file, load_json, save_realy_json_to_file

# Set up basic configuration for logging
logging.basicConfig(
    filename='/Users/paul/paul_data/projects_cs/ba_versuch1/llmedico/data/output/' + 'log.txt',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True
)
logging.debug("---Starting LLMedico---")
logging.debug("---Starting JDoctor - Extracting JavaDoc---")
FQ_CLASS_NAME = "org.apache.commons.lang3.StringUtils"
IMAGE = "pjkroker/toradocu-x86-extractor"
pyjdoctor = PyJDoctor("/Users/paul/paul_data/projects_cs/ba_versuch1/pyjdoctor", IMAGE)
pyjdoctor.set_data_dir("/Users/paul/paul_data/projects_cs/ba_versuch1/llmedico/data")
pyjdoctor.set_output_dir("/Users/paul/paul_data/projects_cs/ba_versuch1/llmedico/data/output")
pyjdoctor.set_input_dir("Users/paul/paul_data/projects_cs/ba_versuch1/llmedico/data/input")

pyjdoctor.start_container()
pyjdoctor.generate_all(FQ_CLASS_NAME)
pyjdoctor.stop_container()

logging.debug("---Starting JavaParser - Extracting JavaDoc---")
jp = JavaParser()
result_json = jp.extract_to_json("/Users/paul/paul_data/projects_cs/ba_versuch1/llmedico/data/input/repository/src/main/java/org/apache/commons/lang3/StringUtils.java")
save_json_to_file(result_json,"/Users/paul/paul_data/projects_cs/ba_versuch1/llmedico/data/output/result.json")
result_json = json.loads(result_json)

logging.debug("---Starting Translator - Translating JavaDoc to Assertions---")
trans = Translator()
LIMIT = 3
results = {}

for i in range(0, LIMIT):
    method_name = result_json[0]["methods"][i]["name"]
    javadoc = result_json[0]["methods"][i]["javadoc"]
    javacode = result_json[0]["methods"][i]["code"]
    java_assertions = trans.translate_javadoc(javacode)
    logging.debug(java_assertions)
    results[method_name] = java_assertions
logging.debug(results)


logging.debug("---Validating Syntax of generated Assertions---")
valid = {}
for method_name in results:
    valid[method_name] = []
    for assertion in results[method_name]:
        if jp.is_valid_java_assert(assertion):
            valid[method_name].append(assertion)
        else:
            logging.debug(f"{assertion} is not a valid java assertion")

logging.debug(valid)

logging.debug("---Adding valid Assertions to Randoop File???---")
#load jdoctor file, remove everything except the one method
#overwrite pre, post and throws with generated assertions
jdoctor = load_json(Path("/Users/paul/paul_data/projects_cs/ba_versuch1/llmedico/data/output/toradocu-randoop_specs.json"))
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
save_realy_json_to_file(specs, "/Users/paul/paul_data/projects_cs/ba_versuch1/llmedico/data/output/" + "specs.json")

rd = PyRandoop(path_output_dir="/Users/paul/paul_data/projects_cs/ba_versuch1/llmedico/data/output",
               class_dir="/Users/paul/paul_data/projects_cs/ba_versuch1/llmedico/data/input/repository/target/classes",
               time_limit=60, deterministic=False)
result = rd.generate_dependencies(
    path_class_file="/Users/paul/paul_data/projects_cs/ba_versuch1/llmedico/data/input/repository/target/classes/org/apache/commons/lang3/StringUtils.class")

result = rd.generate_error_revealing_tests(fq_class_name="org.apache.commons.lang3.StringUtils", path_oracles=Path(
    "/Users/paul/paul_data/projects_cs/ba_versuch1/llmedico/data/output/specs.json"))
logging.debug(result["stdout"])








