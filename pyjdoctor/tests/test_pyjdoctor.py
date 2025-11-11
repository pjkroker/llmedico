from pyjdoctor.pyjdoctor import PyJDoctor
import pathlib


def test_pyjdoctor():
    image_name = "pjkroker/toradocu-x86-extractor"
    pyjdoctor = PyJDoctor("/Users/paul/paul_data/projects_cs/ba_versuch1/pyjdoctor", image_name)

    assert pyjdoctor.__repr__().startswith("PyJDoctor Container mit: image_tag='" + image_name)

def test_extract_java_doc():
    fq_class_name = "org.apache.commons.math3.complex.Complex"
    image_name = "pjkroker/toradocu-x86-extractor"
    pyjdoctor = PyJDoctor("/Users/paul/paul_data/projects_cs/ba_versuch1/pyjdoctor", image_name)
    pyjdoctor.start_container()
    pyjdoctor.extract_java_doc(fq_class_name)

    file_path_condition_translator = pathlib.Path(pyjdoctor.OUT_DIR + "/toradocu-condition_translator.json")
    file_path_javadoc_extractor = pathlib.Path(pyjdoctor.OUT_DIR + "/toradocu-javadoc_extractor.json")
    file_path_randoop_specs = pathlib.Path(pyjdoctor.OUT_DIR + "/toradocu-randoop_specs.json")

    pyjdoctor.stop_container()
    assert file_path_condition_translator.exists(), f"File not found: {file_path_condition_translator.absolute()}"
    assert file_path_javadoc_extractor.exists(), f"File not found: {file_path_javadoc_extractor.absolute()}"
    assert file_path_randoop_specs.exists(), f"File not found: {file_path_randoop_specs.absolute()}"

def test_load_data():
    path = __file__
    data = PyJDoctor._load_data(path)
    assert data is not None
    assert data["name"] == "Paul"