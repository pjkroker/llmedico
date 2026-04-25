import logging
import os
import sys
import json
from pprint import pprint

import docker

from se_helpers.docker_helper import DockerHelper
from se_helpers.subproccess_helper import run_shell


def load_data(file_path):
    # Open the file and load its contents
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data
def main():
    # Ensure the folder exists
    # folder path relative to the script file
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ROOT_DIR = os.path.join(BASE_DIR,"..","..")
    DATA_DIR = os.path.join(ROOT_DIR,"data")
    OUT_DIR = os.path.join(DATA_DIR,"output")
    IN_DIR = os.path.join(DATA_DIR,"input")
    os.makedirs(OUT_DIR, exist_ok=True)
    SETUP_PATH = os.path.join(ROOT_DIR, "scripts", "setup.sh")

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(OUT_DIR, "log.txt"), mode='w'),
            logging.StreamHandler(sys.stdout)
        ],
        force=True
    )
    logging.info("---JavaDoc Extractor---")
    # logging.info("---Building Docker Container using Shell Script---")
    # result = run_shell(f"{SETUP_PATH}", shell=True)
    # logging.debug(result["stdout"])
    # logging.debug(result["stderr"])
    # if (result["returncode"] != 0):
    #     logging.debug(result["returncode"])
    #     sys.exit(result["returncode"])

    logging.info("---Running Docker Container ---")
    IMAGE_TAG = "pjkroker/toradocu-x86-extractor"
    COMMAND = "sleep infinity"
    HOST_VOLUME_PATH = DATA_DIR
    GUEST_VOLUME_PATH = "/data"
    # create helper
    cntr_jdoctor_extractor = DockerHelper()
    cntr_jdoctor_extractor.run_container(IMAGE_TAG, COMMAND, HOST_VOLUME_PATH, GUEST_VOLUME_PATH)
    #cntr_jdoctor_extractor.exec("pwd")
    #cntr_jdoctor_extractor.exec("ls ../toradocu")
    logging.info("---Running Acutal Commands ---")
    FQ_CLASS_NAME = "org.apache.commons.math3.complex.Complex"
    SOURCEDIR_R = "/data/input/repository/src/main/java"
    CLASSDIR_R = "/data/input/repository/target/classes"
    OUTPUTDIR_R = "/data/output"
    JDOC_CMD = f"java -jar /toradocu/build/libs/toradocu-1.0-all.jar --target-class {FQ_CLASS_NAME} --source-dir {SOURCEDIR_R} --class-dir {CLASSDIR_R} --javadoc-extractor-output {os.path.join(OUTPUTDIR_R, 'toradocu-javadoc_extractor.json')} --condition-translator-output {os.path.join(OUTPUTDIR_R, 'toradocu-condition_translator.json')} --randoop-specs {os.path.join(OUTPUTDIR_R, 'toradocu-randoop_specs.json')}"
    JDOC_CMD2 = f"java -jar /toradocu/build/libs/toradocu-1.0-all.jar -h"
    cntr_jdoctor_extractor.exec(JDOC_CMD)
    cntr_jdoctor_extractor.stop_container()

    randoop_specs = load_data(os.path.join(OUT_DIR, "toradocu-randoop_specs.json"))
    print(len(randoop_specs))
    randoop_specs = randoop_specs[0]
    pprint(randoop_specs["operation"])


if __name__ == "__main__":
    main()