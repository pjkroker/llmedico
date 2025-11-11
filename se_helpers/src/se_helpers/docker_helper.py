import logging
import docker
import os
import sys
import json
import tarfile
import io
from pathlib import Path

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class DockerHelper:

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.client = docker.from_env()
        self.logger.info("Docker client initialized")
        self.container = None
    

    #TODO test it 
    def build_container(self, context_path=".", dockerfile="dockerfile", tag="my_docker_file", platform="linux/amd64", log_path="docker_build_log.jsonl"):
        """
        Build a Docker image.

        :param dockerfile: Path to Dockerfile
        :param tag: Image tag
        :param platform: Target platform (e.g., "linux/amd64")
        #:param context: Build context (default ".")
        :return: Built image object
        """
        #os.environ.setdefault("DOCKER_BUILDKIT", "1")
        #os.environ["DOCKER_DEFAULT_PLATFORM"] = "linux/amd64"
        api = docker.APIClient(base_url="unix:///var/run/docker.sock")
        
        

        with open(log_path, "w") as f:
            build_output = api.build(
                path=context_path,
                dockerfile=dockerfile,
                tag=tag,
                platform=platform,
                rm=True,
                decode=True,
            )

            for chunk in build_output:
                # write every JSON chunk to file
                f.write(json.dumps(chunk) + "\n")

                # you can still log selectively
                if "stream" in chunk:
                    self.logger.info(chunk["stream"].rstrip())
                if "error" in chunk:
                    self.logger.error(chunk["error"].rstrip())
    #TODO testing
    def run_container(self, image, command, host_volume_path, guest_volume_path):

        container = self.client.containers.run(
            image=image,
            command=command,  # This is inside the container
            volumes={
                host_volume_path: {  # This is on the host
                    "bind": guest_volume_path,  # This will appear inside the container
                    "mode": "rw"
                }
            },
            tty=True,
            stdin_open=True,
            detach=True,
            stdout=True,  # capture stdout
            stderr=True,
        )
        self.container = container
        return container
    
    #TODO testing
    def exec(self, cmd):
        if self.container is None:
            raise RuntimeError("No container running")

        result = self.container.exec_run(["bash", "-lc", cmd], stdout=True, stderr=True, demux=True)
        out_b, err_b = (result.output or (b"", b""))  # ensure it's always a tuple
        #out_b, err_b = result.output if result.output else (b"", b"")

        # decode safely
        out = out_b.decode(errors="replace") if out_b else ""
        err = err_b.decode(errors="replace") if err_b else ""

        #out = out_b.decode(errors="replace")
        #err = err_b.decode(errors="replace")


        log = True
        if log:
            if out:
                self.logger.info(out.strip())
            if err:
                self.logger.warning(err.strip())
                
        return  {
            "cmd": cmd,
            "exit_code": result.exit_code,
            "stdout": out,
            "stderr": err,
        }


    #TODO testing
    def stop_container(self, remove=True):
        """Cleanup helper."""
        try:
            self.container.remove(force=True) if remove else self.container.stop()
        except Exception:
            pass
    


    def copy_file_from_container(self, container_path: str, host_path: str):
        """
        Copy a single file from inside the container to the host machine.
        
        :param container_path: Full path to the file inside the container (e.g., /app/logs/output.log)
        :param host_path: Destination path on the host (e.g., ./local_logs/output.log)
        """
        if not self.container:
            raise RuntimeError("No container running")
        
        # 1. Get the file as a tar archive from the container
        stream, _ = self.container.get_archive(container_path)

        # 2. Open the tar stream
        tar_bytes = io.BytesIO()
        for chunk in stream:
            tar_bytes.write(chunk)
        tar_bytes.seek(0)

        with tarfile.open(fileobj=tar_bytes) as tar:
            member = tar.getmembers()[0]
            with tar.extractfile(member) as file_content:
                with open(host_path, "wb") as f:
                    f.write(file_content.read())

        self.logger.info(f"Copied {container_path} to {host_path}")

