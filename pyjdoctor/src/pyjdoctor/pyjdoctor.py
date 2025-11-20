import os
import logging
import sys
import json
from pathlib import Path

from se_helpers.docker_helper import DockerHelper


class PyJDoctor:

    def __init__(self, root_dir:str, image_name:str):
        self.ROOT_DIR = root_dir #TODO
        self.DATA_DIR = os.path.join(self.ROOT_DIR, "data")
        self.OUT_DIR = os.path.join(self.DATA_DIR, "output")
        # self.IN_DIR = os.path.join(self.DATA_DIR, "input")
        self.SETUP_PATH = os.path.join(self.ROOT_DIR, "scripts", "setup.sh")

        self.SOURCEDIR_R = "/data/input/repository/src/main/java"
        self.CLASSDIR_R = "/data/input/repository/target/classes"
        self.OUTPUTDIR_R = "/data/output"

        self.container = DockerHelper()
        self.IMAGE_TAG = image_name

        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(self.OUT_DIR, "log.txt"), mode='w'),
                logging.StreamHandler(sys.stdout)
            ],
            force=True
        )
        logging.debug("---PyJDoctor Object initialized---")

    def __repr__(self):
        return f"PyJDoctor Container mit: image_tag='{self.IMAGE_TAG}'root_dir='{self.ROOT_DIR}', image_name='{self.IMAGE_TAG}')"

    def start_container(self):
        logging.info("---Starting PyJDoctor container---")
        COMMAND = "sleep infinity"
        HOST_VOLUME_PATH = self.DATA_DIR
        GUEST_VOLUME_PATH = "/data"
        self.container.run_container(self.IMAGE_TAG, COMMAND, HOST_VOLUME_PATH, GUEST_VOLUME_PATH)

    def execute_cmd(self, cmd:str):
        logging.info("---Executing PyJDoctor command---")
        self.container.exec(cmd)

    def stop_container(self):
        self.container.stop_container()

    def set_output_dir(self, output_dir: Path) -> None:
        self.OUT_DIR = output_dir

    # def set_input_dir(self, input_dir: Path) -> None:
    #     self.IN_DIR = input_dir

    def set_data_dir(self, data_dir: Path) -> None:
        self.DATA_DIR = data_dir


    @staticmethod
    def _load_data(file_path):
        # Open the file and load its contents
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data

    def extract_java_doc(self, fq_class_name):
        JDOC_CMD = f"java -jar /toradocu/build/libs/toradocu-1.0-all.jar --target-class {fq_class_name} --source-dir {self.SOURCEDIR_R} --class-dir {self.CLASSDIR_R} --javadoc-extractor-output {os.path.join(self.OUTPUTDIR_R, 'toradocu-javadoc_extractor.json')}"
        self.execute_cmd(JDOC_CMD)

    def translate_conditions(self, fq_class_name):
        JDOC_CMD = f"java -jar /toradocu/build/libs/toradocu-1.0-all.jar --target-class {fq_class_name} --source-dir {self.SOURCEDIR_R} --class-dir {self.CLASSDIR_R} --condition-translator-output {os.path.join(self.OUTPUTDIR_R, 'toradocu-condition_translator.json')}"
        self.execute_cmd(JDOC_CMD)

    def generate_randoop_specs(self, fq_class_name):
        JDOC_CMD = f"java -jar /toradocu/build/libs/toradocu-1.0-all.jar --target-class {fq_class_name} --source-dir {self.SOURCEDIR_R} --class-dir {self.CLASSDIR_R} --randoop-specs {os.path.join(self.OUTPUTDIR_R, 'toradocu-randoop_specs.json')}"
        self.execute_cmd(JDOC_CMD)

    def generate_all(self, fq_class_name):
        JDOC_CMD = f"java -jar /toradocu/build/libs/toradocu-1.0-all.jar --target-class {fq_class_name} --source-dir {self.SOURCEDIR_R} --class-dir {self.CLASSDIR_R} --javadoc-extractor-output {os.path.join(self.OUTPUTDIR_R, 'toradocu-javadoc_extractor.json')} --condition-translator-output {os.path.join(self.OUTPUTDIR_R, 'toradocu-condition_translator.json')} --randoop-specs {os.path.join(self.OUTPUTDIR_R, 'toradocu-randoop_specs.json')}"
        self.execute_cmd(JDOC_CMD)
