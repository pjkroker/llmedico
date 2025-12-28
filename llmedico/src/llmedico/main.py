import html
import json
from pathlib import Path
from platform import java_ver
from pprint import pprint
import logging
import re

from llm_caller.models.ollama import Ollama
from llm_caller.utils.processing import extract_conditions
from llmedico.builder.class_model_builder import ClassModelBuilder
from llmedico.converters.jdoctor import JDoctorConditionConverter

logger = logging.getLogger(__name__)


from llmedico.java_utils.javapy import JavaParser
from llmedico.translator.translator import Translator, ToradocuCondition
from pyjdoctor.pyjdoctor import PyJDoctor
from pyrandoop.pyrandoop import PyRandoop
from se_helpers.files.files import save_json_to_file, load_json, save_realy_json_to_file


def _normalize_text(text: str) -> str:
    if not text:
        return ""

    # 1. Convert HTML entities (&lt; → <, &gt; → >, etc.)
    text = html.unescape(text)

    # 2. Remove HTML tags (<code>, <p>, etc.) re.sub = regular expressions and substitute
    text = re.sub(r"<[^>]+>", "", text)

    # 3. Normalize whitespace (newlines, multiple spaces, dots, hyphen)
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    text = text.replace(".", " ")
    text = text.replace(",", "")
    text = text.replace("-", "")

    text = text.strip()
    text = text.lower()
    return text

def main(fq_class_name: str, target_method: str, path_data_dir: Path, path_source_dir:Path, path_class_dir: Path, path_output_dir: Path, path_jar: Path):
    relative_path = fq_class_name.replace(".", "/") + ".java"

    if path_data_dir is None:
        pass
    else:
        path_java_class = path_data_dir / "src" / "main" / "java" / relative_path
    # Set up basic configuration for logging
    logging.basicConfig(
        filename=path_output_dir / 'llmedico.log',
        filemode='w',  # overwrite
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        force=True
    )
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


    logger.debug("---Starting LLMedico---")

    logger.debug("---Starting JavaParser - Extracting JavaDoc---")
    #result_json = start_java_parser(path_output_dir, path_java_class)
    jp = JavaParser()
    java_extractions = jp.extract_to_json(path_java_class, path_jar)
    save_json_to_file(java_extractions, path_output_dir / "llmedico-javadoc_extractor.json")
    java_extractions = json.loads(java_extractions) #TODO load var directly and not file


    logger.debug("---Starting Translator - Translating JavaDoc to Conditions---")
    #conditions = start_translator_everything(result_json)
    trans = Translator(Ollama("llama3.1"))
    conditions = []
    logger.debug("translating every method of the class")
    for i in range(0, len(java_extractions[0]["members"])):
        method_name = java_extractions[0]["members"][i]["name"]
        logger.debug(f"current method name: {method_name}")
        javadoc = java_extractions[0]["members"][i]["javadoc"]
        logger.debug(f"has the following javadoc: {javadoc}")
        parameters = java_extractions[0]["members"][i]["parameters"]
        type = java_extractions[0]["members"][i]["type"]

        # get modes {PARAM, RETURN, THROWS} and their #tags in the doctring
        modes = {}
        for tag in java_extractions[0]["members"][i]["tags"]:
            key = tag["tag"].upper()
            modes[key] = modes.get(key, 0) + 1
        if not modes: logger.warning(f"{method_name} contains not tags?")  # TODO improve, what to do in this case
        logger.debug(f"found modes and their frequencies: {modes}")

        java_assertions = trans.translate_javadoc(javadoc, parameters, modes=modes)
        logger.debug(f"the following java assertion have been generated for {modes} for {method_name}:\n {java_assertions}")
        member = {"method": method_name, "type": type, "parameters": parameters, "conditions": java_assertions}
        conditions.append(member)

    save_realy_json_to_file(conditions, path_output_dir / "llmedico-conditions.json")
    logger.debug(f"the following java assertions have been generated for {fq_class_name}: \n {conditions}")


    logger.debug("---Inserting Generated Conditions into LLMedico File---")
    #conditions = load_json(path_output_dir / "llmedico-conditions.json")

    for i, member in enumerate(java_extractions[0]["members"]):
        for j, tag in enumerate(member["tags"]):
            for condition in conditions[i]["conditions"][tag["tag"].upper()]:
                if (tag["name"] == condition["name"]
                        and (not tag["name"] == "throws" or _normalize_text(tag["content"]) == _normalize_text(condition["content"]))): #two @throws can have same name (exception)
                    tag["assertion"] = condition["assertion"]
                    tag["description"] = condition["description"]

    # check if there is now an assertion for every tag, if not llm has most likely extracted content poorly
    for member in java_extractions[0]["members"]:
        for tag in member["tags"]:
            if len(tag) != 5:
                logger.critical(f"insertion failed for {tag}") #TODO what to do in this case?

    # Convert to pretty JSON string for logging
    json_preview = json.dumps(java_extractions, indent=2, ensure_ascii=False)
    logger.info("Data before dumping:\n%s", json_preview)
    save_realy_json_to_file(java_extractions, path_output_dir / "llmedico-condition_translator.json")

    llmedico_trans_conditions = java_extractions


    logger.debug("---Loading Data from LLMedico File into internal Canonical State---")
    builder = ClassModelBuilder()
    cls = builder.build_class(llmedico_trans_conditions[0])

    logger.debug("---Converting Data from Canonical State into JDoctor Format---")
    jdoc_converter = JDoctorConditionConverter()
    jdoc_trans_conditions = jdoc_converter.convert_class(cls)
    save_realy_json_to_file(jdoc_trans_conditions, path_output_dir / "test_llmedico_conditions_jdoc_format.json")

    logger.debug("---Ending LLMedico---")


if __name__ == '__main__':
    FQ_CLASS_NAME = "org.jgrapht.alg.AbstractPathElementList"  # --target-class java class to be analyzed
    TARGET_METHOD = "isPrimee"  # --target-method#
    PATH_DATA_DIR = Path(
        "/Users/paul/paul_data/projects_cs/ba_versuch1/pyjdoctor/data/input/jgrapht-jgrapht-0.9.2/jgrapht-core")  # --data-dir
    path_jar = Path(
        "/Users/paul/paul_data/projects_cs/ba_versuch1/pyjdoctor/data/input/jgrapht-jgrapht-0.9.2/jgrapht-core/target/jgrapht-core-0.9.2.jar")

    PATH_SOURCE_DIR = None #--source-dir and #--class-dir if no --data-dir was provided
    PATH_CLASS_DIR = None #TODO change if source and class are NOT in the same directory

    PATH_OUTPUT_DIR = Path(
        "/Users/paul/paul_data/projects_cs/ba_versuch1/llmedico/data/output")  # --out-dir

    main(fq_class_name=FQ_CLASS_NAME,
         target_method=TARGET_METHOD,
         path_data_dir=PATH_DATA_DIR if PATH_DATA_DIR else None,
         path_source_dir=PATH_SOURCE_DIR,
         path_class_dir=PATH_CLASS_DIR,
         path_output_dir=PATH_OUTPUT_DIR,
         path_jar=path_jar,)
