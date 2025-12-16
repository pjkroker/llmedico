import os
import logging
import sys
import json
from pathlib import Path

from pyjdoctor.jdoctor_metrics import compute_metrics
from se_helpers.docker_helper import DockerHelper


class PyJDoctor:

    def __init__(self, root_dir:str, image_name:str, path_data_dir, path_output_dir):
        self.ROOT_DIR = root_dir #TODO remove?
        self.DATA_DIR = os.path.join(self.ROOT_DIR, "data") #TODO remove?
        self.OUT_DIR = path_output_dir
        self.IN_DIR = path_data_dir
        self.SETUP_PATH = os.path.join(self.ROOT_DIR, "scripts", "setup.sh")

        #inside the container
        self.INPUT_DIR_R = "/input"
        self.OUTPUTDIR_R = "/output"

        self.SOURCEDIR_R = "/input/src/main/java" #set manually if not at this location
        self.CLASSDIR_R = "/input/target/classes" #set manually if not at this location


        self.container = DockerHelper()
        self.IMAGE_TAG = image_name

        # logging.basicConfig(
        #     level=logging.DEBUG,
        #     format='%(asctime)s - %(levelname)s - %(message)s',
        #     handlers=[
        #         logging.FileHandler(os.path.join(self.OUT_DIR, "log.txt"), mode='w'),
        #         logging.StreamHandler(sys.stdout)
        #     ],
        #     force=True
        # )
        logging.debug("---PyJDoctor Object initialized---")

    def __repr__(self):
        return f"PyJDoctor Container mit: image_tag='{self.IMAGE_TAG}'root_dir='{self.ROOT_DIR}', image_name='{self.IMAGE_TAG}')"

    def start_container(self):
        logging.info("---Starting PyJDoctor container---")
        COMMAND = "sleep infinity"

        path_host_input = self.IN_DIR
        path_guest_input = self.INPUT_DIR_R

        path_host_output = self.OUT_DIR
        path_guest_output = self.OUTPUTDIR_R

        logging.debug(path_host_output)
        logging.debug(path_guest_output)
        logging.debug(path_guest_input)
        logging.debug(path_host_input)

        self.container.run_container_two_mounts(self.IMAGE_TAG, COMMAND, path_host_input, path_guest_input, path_host_output, path_guest_output)

    def execute_cmd(self, cmd:str):
        logging.info("---Executing PyJDoctor command---")
        self.container.exec(cmd)

    def stop_container(self):
        self.container.stop_container()

    def set_output_dir(self, output_dir: Path) -> None:
        self.OUT_DIR = output_dir

    def set_input_dir(self, input_dir: Path) -> None:
        self.IN_DIR = input_dir

    def set_data_dir(self, data_dir: Path) -> None:
        self.DATA_DIR = data_dir

    def set_source_dir_r(self, source_dir: Path) -> None:
        self.SOURCEDIR_R = source_dir
    def set_class_dir_r(self, class_dir: Path) -> None:
        self.CLASSDIR_R = class_dir


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
        JDOC_CMD = f"java -jar /toradocu/build/libs/toradocu-1.0-all.jar --target-class {fq_class_name} --source-dir {self.SOURCEDIR_R} --class-dir {self.CLASSDIR_R} --javadoc-extractor-output {os.path.join(self.OUTPUTDIR_R, 'toradocu-javadoc_extractor.json')} --condition-translator-output {os.path.join(self.OUTPUTDIR_R, 'toradocu-condition_translator.json')} --randoop-specs {os.path.join(self.OUTPUTDIR_R, 'toradocu-randoop_specs.json')} --stats-file {os.path.join(self.OUTPUTDIR_R, 'stats.csv')}"
        logging.debug(JDOC_CMD)
        self.execute_cmd(JDOC_CMD)

    def generate_statistics(self, fq_class_name, expected_conditions_path: Path):
        JDOC_CMD = f"java -jar /toradocu/build/libs/toradocu-1.0-all.jar --target-class {fq_class_name} --source-dir {self.SOURCEDIR_R} --class-dir {self.CLASSDIR_R} --expected-output {expected_conditions_path} --stats-file {os.path.join(self.OUTPUTDIR_R, 'stats.csv')}"
        #--stats-file {os.path.join(self.OUTPUTDIR_R, 'stats.csv')} --condition-translator-output {os.path.join(self.OUTPUTDIR_R, 'toradocu-condition_translator.json')} --condition-translator-input {os.path.join(self.OUTPUTDIR_R, 'toradocu-condition_translator.json')}
        logging.debug(JDOC_CMD)
        self.execute_cmd(JDOC_CMD)

    @staticmethod
    def compute_metrics(csv_path: Path, additional_missing: int=0):
        return compute_metrics(csv_path, additional_missing=additional_missing)
