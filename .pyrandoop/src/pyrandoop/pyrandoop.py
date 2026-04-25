from pathlib import Path

from se_helpers.files.files import save_json_to_file
from se_helpers.subproccess_helper import run_shell

class PyRandoop(object):
    PATH_RANDOOP_JAR = Path("/.pyrandoop/data/jars/randoop-all-4.3.4.jar")
    def __init__(self, seed=0, path_classlist=None, time_limit=0, path_output_dir=None, deterministic=True, attempted_limit=1000000, class_dir=None, class_file=None):
        self.seed = seed
        self.path_classlist = path_classlist
        self.time_limit = time_limit #default: 100 (If nonzero, Randoop is nondeterministic)
        self.path_output_dir = Path(path_output_dir)
        self.deterministic = deterministic
        self.attempted_limit = attempted_limit #default: 100000000
        self.path_class_dir = class_dir
        self.path_class_file = class_file

    def get_path_output_dir(self) -> Path:
        return self.path_output_dir
    def get_path_classlist(self) -> Path:
        return self.path_classlist

    def generate_dependencies(self, path_class_file: Path) -> str:#or methodlist
        result = run_shell(
            f"jdeps -apionly -v -R -cp {self.path_class_dir} {path_class_file} | grep -v '^[A-Za-z]' | sed -E 's/^.* -> ([^ ]+) .*$/\\1/' | sort | uniq",
            shell=True)
        save_json_to_file(result["stdout"], self.path_output_dir / "methodlist.txt")
        dependencies = result["stdout"]
        return dependencies

    def generate_regression_tests(self, fq_class_name: Path) -> dict:
        result = run_shell(
        f"java --class-path {self.PATH_RANDOOP_JAR}:{self.path_class_dir} randoop.main.Main gentests --testclass={fq_class_name} --classlist={self.path_output_dir / 'methodlist.txt'} --time-limit={self.time_limit} --stop-on-error-test --use-jdk-specifications=false --error-test-basename=ErrorTest --junit-output-dir={self.path_output_dir} --deterministic={self.deterministic} --attempted-limit={self.attempted_limit}",
            shell=True)
        return result

    def generate_error_revealing_tests(self, fq_class_name, path_oracles: Path) -> dict:
        result = run_shell(
            f"java --class-path {self.PATH_RANDOOP_JAR}:{self.path_class_dir} randoop.main.Main gentests --testclass={fq_class_name} --classlist={self.path_output_dir / 'methodlist.txt'} --time-limit={self.time_limit} --stop-on-error-test --use-jdk-specifications=false --error-test-basename=ErrorTest --specifications={path_oracles} --junit-output-dir={self.path_output_dir} --deterministic={self.deterministic} --attempted-limit={self.attempted_limit}",
            shell=True)
        return result

    def _check_java_installation(self):
        raise NotImplementedError