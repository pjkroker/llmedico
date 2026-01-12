import os
from pathlib import Path

from llmedico.main import main
import datetime

from pyjdoctor.pyjdoctor import PyJDoctor

input_ = Path(__file__).parent.parent.parent / "pyjdoctor" / "data" / "input"

LLMEDICO = True
JDOCTOR = False

projects = {"commons-collections4-4.1":
                {"data_dir": input_ / "commons-collections4-4.1-src" / "src",
                 "jar_dir": input_ / "commons-collections4-4.1-src" / "target" / "commons-collections4-4.1.jar",
                 "jdoc_data_dir_a": input_ / "commons-collections4-4.1-src",
                 "jdoc_source_dir_r": "/input/src/main/java",
                 "jdoc_class_dir_r": "/input/target/classes"},
            "commons-math3-3.6.1":{
                "data_dir": input_ / "commons-math3-3.6.1-src" / "src",
                "jar_dir": input_ / "commons-math3-3.6.1-src" / "target" / "commons-math3-3.6.1.jar",
                "jdoc_data_dir_a": input_ / "commons-math3-3.6.1-src",
                "jdoc_source_dir_r": "/input/src/main/java",
                "jdoc_class_dir_r": "/input/target/classes"},
            "freecol-0.11.6":{
                "data_dir": input_ / "freecol-0.11.6" / "src",
                "jar_dir": input_ / "freecol-0.11.6" / "FreeCol.jar",
                "jdoc_data_dir_a": input_ / "freecol-0.11.6",
                "jdoc_source_dir_r": "/input/src/",
                "jdoc_class_dir_r": "/input/build"},
            "gs-core-1.3": {
                "data_dir": input_ / "gs-core-1.3" / "gs-core-1.3-sources",
                "jar_dir": input_ / "gs-core-1.3" / "gs-core-1.3.jar",
                "jdoc_data_dir_a": input_ / "gs-core-1.3",
                "jdoc_source_dir_r": "/input/gs-core-1.3-sources/",
                "jdoc_class_dir_r": "/input/gs-core-1.3"},
            "guava-19.0": {
                "data_dir": input_ / "guava-19.0" / "guava" / "src",
                "jar_dir": input_ / "guava-19.0" / "guava" / "target" / "guava-19.0.jar",
                "jdoc_data_dir_a": input_ / "guava-19.0",
                "jdoc_source_dir_r": "/input/guava/src",
                "jdoc_class_dir_r": "/input/guava/target/classes"},
            "jgrapht-core-0.9.2": {
                "data_dir": input_ / "jgrapht-0.9.2" / "jgrapht-core" / "src",
                "jdoc_data_dir_a": input_ / "jgrapht-0.9.2" / "jgrapht-core",
                "jdoc_source_dir_r": "/input/src/main/java",
                "jdoc_class_dir_r" : "/input/target/classes",
                "jar_dir": input_ / "jgrapht-0.9.2" / "jgrapht-core" / "target" / "jgrapht-core-0.9.2.jar",
                "class_dir": input_ / "jgrapht-0.9.2" / "jgrapht-core" / "target" / "classes"},
            "plume-lib-1.1.0": {
                "data_dir": input_ / "plume-lib-1.1.0" / "java" / "src",
                "jar_dir": input_ / "plume-lib-1.1.0" / "java" / "plume.jar",
                "jdoc_data_dir_a": input_ / "plume-lib-1.1.0" / "java" / "src",
                "jdoc_source_dir_r": "/input/",
                "jdoc_class_dir_r": "/input/"
            }
            }

done = []

date = datetime.date.today()

for project in projects:
    if project not in done:
        print(f"Running {project}...")
        if not projects[project]["data_dir"].is_dir():
            print(f"{projects[project]['data_dir']} not found, skipping")
            raise FileNotFoundError
        if not projects[project]["jar_dir"].exists():
            print(f"{projects[project]['jar_dir']} not found, skipping")
            raise FileNotFoundError
        path_classes = Path(__file__).parent.parent / "storage" / "projects_txt" / (project + ".txt")
        if not path_classes.exists():
            print(f"{path_classes} not found, skipping")
            raise FileNotFoundError
        with path_classes.open("r", encoding="utf-8") as f:
            classes_ = [line.strip() for line in f if line.strip()]

        for class_ in classes_:
            if LLMEDICO:
                if class_ not in done:
                    base_result = Path(__file__).parent / "results-translation" / (project + "-" + str(date))
                    path_out_dir = base_result / class_

                    if not path_out_dir.exists():
                        os.makedirs(path_out_dir)
                    main(fq_class_name=class_,
                         target_method="dummy",
                         path_data_dir=None,
                         path_source_dir=projects[project]["data_dir"],
                         path_class_dir=None,
                         path_output_dir=path_out_dir,
                         path_jar=projects[project]["jar_dir"])
            if JDOCTOR:
                if class_ not in done:
                    base_result = Path(__file__).parent / "results-translation-jdoctor" / (project + "-" + str(date))
                    path_out_dir = base_result / class_

                    if not path_out_dir.exists():
                        os.makedirs(path_out_dir)

                    jdoc = PyJDoctor("", "pjkroker/toradocu-3.0-x86", projects[project]["jdoc_data_dir_a"], path_out_dir)
                    jdoc.set_source_dir_r(projects[project]["jdoc_source_dir_r"])
                    jdoc.set_class_dir_r(projects[project]["jdoc_class_dir_r"])

                    jdoc.start_container()
                    jdoc.generate_all(class_)
                    jdoc.stop_container()



