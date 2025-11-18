import json

from llmedico.java_utils.javapy import JavaParser
from llmedico.java_utils.translator.translator import Translator
from pyjdoctor.pyjdoctor import PyJDoctor
import logging

from se_helpers.files.files import save_json_to_file

# Set up basic configuration for logging
logging.basicConfig(
    #filename='log.txt',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True
)
logging.debug("---Starting LLMedico---")
# logging.debug("---Starting JDoctor - Extracting JavaDoc---")
# FQ_CLASS_NAME = "org.apache.commons.lang3.StringUtils"
# IMAGE = "pjkroker/toradocu-x86-extractor"
# pyjdoctor = PyJDoctor("/Users/paul/paul_data/projects_cs/ba_versuch1/pyjdoctor", IMAGE)
# pyjdoctor.set_data_dir("/Users/paul/paul_data/projects_cs/ba_versuch1/llmedico/data")
# pyjdoctor.set_output_dir("/Users/paul/paul_data/projects_cs/ba_versuch1/llmedico/data/output")
# pyjdoctor.set_input_dir("Users/paul/paul_data/projects_cs/ba_versuch1/llmedico/data/input")
#
# pyjdoctor.start_container()
# pyjdoctor.generate_all(FQ_CLASS_NAME)
# pyjdoctor.stop_container()

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
    print(java_assertions)
    results[method_name] = java_assertions

print(results)

logging.debug("---Validating Syntax of generated Assertions---")
valid = {}
for method_name in results:
    valid[method_name] = []
    for assertion in results[method_name]:
        if jp.is_valid_java_assert(assertion):
            valid[method_name].append(assertion)
        else:
            print(f"{assertion} is not a valid java assertion")

print(valid)
logging.debug("---Adding valid Assertions to Randoop File???---")










