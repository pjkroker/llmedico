import subprocess
import os

def run(command, args):
    """
    Runs a binary as a new subprocess and returns standard information about the process.
    Args:
            command (str): The command.
            args (list[str]): List of command-line arguments.
    Returns:
            dict: A dictionary containing:
                - 'stdout' (str): Standard output from the process.
                - 'stderr' (str): Standard error from the process.
                - 'returncode' (int): Exit code returned by the process.
                - 'pid' (int): Process ID of the launched subprocess.
    """
    # Launch the subprocess
    proc = subprocess.Popen(
        [command] + args,  # Combine binary path with argument list
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    # Wait for the process to finish and capture output
    stdout, stderr = proc.communicate()

    # Package result similar to subprocess.run()
    result = {
        "stdout": stdout,
        "stderr": stderr,
        "returncode": proc.returncode,
        "pid": proc.pid
    }
    return result

def run_shell(command, shell=False):
    """
    Runs a command with optional shell interpretation.
    Args:
        command (str or list): Command to run. If shell=True, must be str.
        shell (bool): Whether to run command through the shell.
    Returns:
        dict: Contains stdout, stderr, returncode, pid.
    """
    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=shell
    )
    stdout, stderr = proc.communicate()
    return {
        "stdout": stdout,
        "stderr": stderr,
        "returncode": proc.returncode,
        "pid": proc.pid
    }

def run_async2(command, args):
    """
    Launches a subprocess asynchronously (non-blocking).
    Returns the Popen object so the caller can manage it.
    """
    proc = subprocess.Popen(
        [command] + args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return proc


def run_async(command, args, logfile=False, logfile_path="./out/subprocess.log"):
    """
    Launches a subprocess asynchronously (non-blocking).
    If logfile=True, all output is written directly to logfile_path.
    Otherwise, stdout/stderr are piped.
    """
    if logfile:
        os.makedirs(os.path.dirname(logfile_path), exist_ok=True)
        f = open(logfile_path, "a", buffering=1)  # line-buffered
        proc = subprocess.Popen(
            [command] + args,
            stdout=f,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        # keep file handle on proc so caller can close later if desired
        proc.logfile = f
    else:
        proc = subprocess.Popen(
            [command] + args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
    return proc