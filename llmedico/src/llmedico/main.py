from llmedico.java_utils.javapy import JavaParser
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
logging.debug("---Starting JDoctor - Extracting JavaDoc---")
fq_class_name = "org.apache.commons.math3.complex.Complex"
image_name = "pjkroker/toradocu-x86-extractor"
pyjdoctor = PyJDoctor("/Users/paul/paul_data/projects_cs/ba_versuch1/pyjdoctor", image_name)
pyjdoctor.set_data_dir("/Users/paul/paul_data/projects_cs/ba_versuch1/llmedico/data")
pyjdoctor.set_output_dir("/Users/paul/paul_data/projects_cs/ba_versuch1/llmedico/data/output")
pyjdoctor.set_input_dir("Users/paul/paul_data/projects_cs/ba_versuch1/llmedico/data/input")
pyjdoctor.start_container()
pyjdoctor.generate_all(fq_class_name)
pyjdoctor.stop_container()

logging.debug("---Starting 2. - Extracting JavaDoc---")
jp = JavaParser()
result_json = jp.extract_to_json("/Users/paul/paul_data/projects_cs/ba_versuch1/llmedico/tests/data/input/TestJavaAssertion.java")
save_json_to_file(result_json,"/Users/paul/paul_data/projects_cs/ba_versuch1/llmedico/data/output/result.json")




