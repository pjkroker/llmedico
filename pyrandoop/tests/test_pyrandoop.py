from pathlib import Path

from pyrandoop.pyrandoop import PyRandoop


def test_pyrandoop_generate_dependencies():
    rd = PyRandoop(path_output_dir="/Users/paul/paul_data/projects_cs/ba_versuch1/pyrandoop/data/output",
                   class_dir="/Users/paul/paul_data/projects_cs/ba_versuch1/pyrandoop/data/input/repository/target/classes",
                   )
    result = rd.generate_dependencies(path_class_file="/Users/paul/paul_data/projects_cs/ba_versuch1/pyrandoop/data/input/repository/target/classes/org/apache/commons/lang3/StringUtils.class")
    assert result == "java.io.UnsupportedEncodingException\njava.lang.CharSequence\njava.lang.Deprecated\njava.lang.Iterable\njava.lang.Object\njava.lang.SafeVarargs\njava.lang.String\njava.nio.charset.Charset\njava.util.Iterator\njava.util.Locale\n"
    assert Path("/Users/paul/paul_data/projects_cs/ba_versuch1/pyrandoop/data/output/methodlist.txt").exists()

def test_pyrandoop_generate_error_revealing_tests():
    rd = PyRandoop(path_output_dir="/Users/paul/paul_data/projects_cs/ba_versuch1/pyrandoop/data/output",
                   class_dir="/Users/paul/paul_data/projects_cs/ba_versuch1/pyrandoop/data/input/repository/target/classes",
                   )
    result = rd.generate_dependencies(
        path_class_file="/Users/paul/paul_data/projects_cs/ba_versuch1/pyrandoop/data/input/repository/target/classes/org/apache/commons/lang3/StringUtils.class")
    result = rd.generate_error_revealing_tests(fq_class_name="org.apache.commons.lang3.StringUtils", path_oracles=Path("/Users/paul/paul_data/projects_cs/ba_versuch1/pyrandoop/data/input/toradocu-randoop_specs.json"))
    assert Path(rd.get_path_output_dir() / "ErrorTest.java").exists()
    assert Path(rd.get_path_output_dir() / "RegressionTest.java").exists()
    assert result["stdout"].startswith("Randoop for Java version 4.3.4.")
    assert result["stdout"].endswith("Invalid tests generated: 0\n")
