import logging
from pathlib import Path

#from pyjdoctor import PyJDoctor
from pyjdoctor.pyjdoctor import PyJDoctor
#from jdoctor_metrics import compute_metrics


def main(fq_class_name: str, path_data_dir: Path, path_source_dir, path_class_dir, path_output_dir: Path) -> None:
    jdoc = PyJDoctor("", "pjkroker/toradocu-3.0-x86", path_data_dir, path_output_dir)

    jdoc.start_container()
    #jdoc.translate_conditions(fq_class_name)
    jdoc.generate_statistics(fq_class_name,"/input/org.apache.commons.math3.primes.Primes_goal.json")
    metrics = jdoc.compute_metrics(path_output_dir / "stats.csv")
    # jdoc.generate_statistics(fq_class_name, "/input/llmedico-toradocu-condition_translator.json")
    # jdoc.stop_container()
    metrics = jdoc.compute_metrics(path_output_dir / "stats.csv")



if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fq_class_name = "org.apache.commons.math3.primes.Primes"
    path_data_dir = Path(__file__).parent.parent / "data" / "input" / "commons-math3-3.6.1-src"
    path_source_dir = ""
    path_class_dir = ""
    path_output_dir = Path(__file__).parent.parent / "data" / "output"
    main(fq_class_name, path_data_dir, path_source_dir, path_class_dir, path_output_dir)