import html
import json
import os
from pathlib import Path
import logging
import re

from llm_caller.models.litellm import LiteLLMModel
from llm_caller.models.ollama import Ollama
from llmedico.builder.class_model_builder import ClassModelBuilder
from llmedico.conditions.model import ConditionKind
from llmedico.config.config import Config
from llmedico.converters.jdoctor import JDoctorConditionConverter
from llmedico.translator.method_selector import MethodSelector

logger = logging.getLogger(__name__)


from llmedico.java_utils.javapy import JavaParser
from llmedico.translator.translator import Translator
from se_helpers.files.files import save_json_to_file, save_realy_json_to_file, load_json


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

def main(fq_class_name: str, target_method: str | None, path_source_dir:Path, path_output_dir: Path, path_jar: Path):
    if "$" in fq_class_name:
        containsNestedClasses = True
        relative_path = fq_class_name.split("$")[0].replace(".", "/") + ".java"
        inner_class_name = fq_class_name.split("$")[1]
    else:
        containsNestedClasses = False
        relative_path = fq_class_name.replace(".", "/") + ".java"

    path_java_class = path_source_dir / relative_path
    # if path_data_dir is None:
    #     path_java_class = path_source_dir / relative_path #TODO add "main" / "java" to path in run
    # else:
    #     path_java_class = path_data_dir / relative_path#/ "src" / "main" / "java" / relative_path
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
    config_path = Path(
        os.getenv("LLMEDICO_CONFIG", Path.cwd() / "config.toml") #TODO test environment variable
    ).expanduser().resolve()

    cnfg = Config(config_path)
    llm_config = cnfg.section("llm")
    trans_config = cnfg.section("translation")

    logger.debug("---Starting JavaParser - Extracting JavaDoc---")
    #result_json = start_java_parser(path_output_dir, path_java_class)
    jp = JavaParser()
    java_extractions = jp.extract_to_json(path_java_class, path_jar)
    if containsNestedClasses:
        java_extractions = json.loads(java_extractions)
        java_extractions = [class_ for class_ in java_extractions if class_["name"] == inner_class_name]
        java_extractions[0]["qualified_name"] = fq_class_name #add part with "$" again
        java_extractions = json.dumps(java_extractions)

    save_json_to_file(java_extractions, path_output_dir / "llmedico-javadoc_extractor.json")
    java_extractions = json.loads(java_extractions) #TODO load var directly and not file


    logger.debug("---Starting Translator - Translating JavaDoc to Conditions---")
    if "/" not in llm_config["model"]:
        llm = Ollama(llm_config["model"], temperature=llm_config["temperature"])
    else:
        llm = LiteLLMModel(model_name=llm_config["model"], api_base=llm_config["LITELLM_API_BASE"], api_key="dummy") #TODO check LiteLLM compability
    trans = Translator(llm, trans_config["iteration_repairloop"])
    conditions = []
    logger.debug("translating every method of the class")

    #build class model TODO make this consistent
    builder = ClassModelBuilder()
    with open(path_output_dir / "llmedico-javadoc_extractor.json", "r", encoding="utf-8") as f:
        extracted_conditions = json.load(f)
    cls = builder.build_class(extracted_conditions[0])
    #select methods
    selector = MethodSelector(cls)
    method_selection = selector.get_methods_to_str()

    for i in range(0, len(java_extractions[0]["members"])):
        method_name = java_extractions[0]["members"][i]["name"]
        logger.debug(f"current method name: {method_name}")
        javadoc = java_extractions[0]["members"][i]["javadoc"]
        logger.debug(f"has the following javadoc: {javadoc}")
        parameters = java_extractions[0]["members"][i]["parameters"]
        return_type = java_extractions[0]["members"][i].get("return_type", None)
        tags = java_extractions[0]["members"][i]["tags"]
        type = java_extractions[0]["members"][i]["type"]

        # get modes {PARAM, RETURN, THROWS} and their #tags in the docstring
        modes = {}
        for tag in java_extractions[0]["members"][i]["tags"]:
            if ConditionKind.is_condition_kind(tag["tag"]):
                key = tag["tag"].upper()
                modes[key] = modes.get(key, 0) + 1
            else:
                logger.debug(f"unsupported tag: {tag}")
        if not modes: logger.warning(f"{method_name} contains not tags?")  # TODO improve, what to do in this case
        logger.debug(f"found modes and their frequencies: {modes}")

        java_assertions = trans.translate_javadoc(javadoc, method_name, parameters, return_type, method_selection, tags, modes=modes)
        logger.debug(f"the following java assertion have been generated for {modes} for {method_name}:\n {java_assertions}")
        member = {"method": method_name, "type": type, "parameters": parameters, "conditions": java_assertions}
        conditions.append(member)

    save_realy_json_to_file(conditions, path_output_dir / "llmedico-conditions.json")
    logger.debug(f"the following java assertions have been generated for {fq_class_name}: \n {conditions}")


    logger.debug("---Inserting Generated Conditions into LLMedico File---")
    #conditions = load_json(path_output_dir / "llmedico-conditions.json")

    for i, member in enumerate(java_extractions[0]["members"]):
        for j, tag in enumerate(member["tags"]):
            if ConditionKind.is_condition_kind(tag["tag"]): #skip unsuported ones like @see
                for condition in conditions[i]["conditions"][tag["tag"].upper()]:
                    if (tag["name"] == condition["name"]
                            and (not tag["tag"] == "throws" or len(conditions[i]["conditions"][tag["tag"].upper()]) == 1 #two @throws can have same name (exception)
                                 or _normalize_text(tag["content"]) == _normalize_text(condition["content"]))): #if there's more than one, make sure content is equal
                        tag["assertion"] = condition["assertion"]
                        tag["description"] = condition["description"]

    # check if there is now an assertion for every tag, if not llm has most likely extracted content poorly
    for member in java_extractions[0]["members"]:
        for tag in member["tags"]:
            if ConditionKind.is_condition_kind(tag["tag"]):  # skip unsupported ones like @see
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
    FQ_CLASS_NAME = "net.sf.freecol.common.model.Player$ActivePredicate"  # --target-class java class to be analyzed
    TARGET_METHOD = "isPrimee"  # --target-method#
    PATH_SOURCE_DIR = Path("/Users/paul/paul_data/projects_cs/ba_versuch1/pyjdoctor/data/input/freecol-0.11.6/src")
    PATH_JAR = Path(
        "/Users/paul/paul_data/projects_cs/ba_versuch1/pyjdoctor/data/input/freecol-0.11.6/FreeCol.jar")
    PATH_OUTPUT_DIR = Path(__file__).parent.parent.parent / "data" / "output" # --out-dir

    os.environ["LLMEDICO_CONFIG"] = (Path(__file__).parent.parent.parent / "config.toml").as_posix()

    #PATH_DATA_DIR = Path(
    #    "/Users/paul/paul_data/projects_cs/ba_versuch1/pyjdoctor/data/input/freecol-0.11.6/src")  # --data-dir
    #/pyjdoctor/data/input/commons-collections4-4.1-src/src/main/java
    #PATH_CLASS_DIR = None #TODO change if source and class are NOT in the same directory

    main(fq_class_name=FQ_CLASS_NAME,
         target_method=TARGET_METHOD,
         path_source_dir=PATH_SOURCE_DIR,  #TODO use only src dir
         path_output_dir=PATH_OUTPUT_DIR,
         path_jar=PATH_JAR)
