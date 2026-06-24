""" Wrapper for calling Chapel drivers.
"""
# std imports
import copy
import logging
import os
from os import PathLike
import subprocess
import sys
import tempfile

# local imports
sys.path.append("..")
from drivers.driver_wrapper import DriverWrapper, BuildOutput, RunOutput, GeneratedTextResult
from util import run_command

""" Map parallelism models to driver file basenames """
DRIVER_MAP = {
    "chapel": "driver.chpl",
}

""" Default compiler settings """
COMPILER_SETTINGS = {
    "chapel": {"CHPL": "chpl", "CHPLFLAGS": "--fast"},
}


class ChapelDriverWrapper(DriverWrapper):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_configs = self.build_configs or COMPILER_SETTINGS
        self.model_driver_file = DRIVER_MAP[self.parallelism_model]

    def write_source(self, content: str, fpath: PathLike) -> bool:
        with open(fpath, "w") as fp:
            fp.write(content)
        return True

    def compile(
        self,
        *sources: PathLike,
        output_path: PathLike = "a.out",
        CHPL: str = "chpl",
        CHPLFLAGS: str = "--fast",
        **kwargs,
    ) -> BuildOutput:
        sources_str = " ".join(sources)
        cmd = f"{CHPL} {CHPLFLAGS} -o {output_path} {sources_str}"
        try:
            result = run_command(cmd, timeout=self.build_timeout, dry=self.dry)
            logging.debug(f"Chapel build stdout: {result.stdout}  stderr: {result.stderr}")
        except subprocess.TimeoutExpired as e:
            return BuildOutput(-1, str(e.stdout), f"[Timeout] {str(e.stderr)}")
        return BuildOutput(result.returncode, result.stdout, result.stderr)

    def run(self, executable: PathLike, problem_size_int: int = None, **run_config) -> RunOutput:
        launch_format = self.launch_configs["format"]
        args = f"--problemSize={problem_size_int}" if problem_size_int is not None else ""
        launch_cmd = launch_format.format(exec_path=executable, args=args, **run_config).strip()
        logging.debug(f"Chapel launch cmd: {launch_cmd}")
        try:
            run_process = run_command(launch_cmd, timeout=self.run_timeout, dry=self.dry)
        except subprocess.TimeoutExpired as e:
            return RunOutput(-1, str(e.stdout), f"[Timeout] {str(e.stderr)}", config=run_config)
        except UnicodeDecodeError as e:
            return RunOutput(-1, "", f"UnicodeDecodeError: {str(e)}", config=run_config)
        return RunOutput(run_process.returncode, run_process.stdout, run_process.stderr, config=run_config)

    def test_single_output(
        self,
        prompt: str,
        output: str,
        test_driver_file: PathLike,
        problem_size: str,
        problem_type: str,
    ) -> GeneratedTextResult:
        logging.debug(f"Testing Chapel output:\n{output}")
        with tempfile.TemporaryDirectory(dir=self.scratch_dir) as tmpdir:
            src_path = os.path.join(tmpdir, "generated-code.chpl")
            write_success = self.write_source(output, src_path)

            exec_path = os.path.join(tmpdir, "a.out")
            compiler_kwargs = copy.deepcopy(self.build_configs[self.parallelism_model])

            build_result = self.compile(
                test_driver_file, src_path, output_path=exec_path, **compiler_kwargs
            )
            logging.debug(f"Chapel build result: {build_result}")
            if self.display_build_errors and build_result.stderr and not build_result.did_build:
                logging.debug(build_result.stderr)
                print("DID NOT BUILD")

            if not build_result.did_build:
                return GeneratedTextResult(write_success, build_result, None)

            # Evaluate problem_size expression (e.g. "(1<<18)") to an integer.
            try:
                ps_int = int(eval(problem_size))
            except Exception:
                ps_int = 1 << 18

            configs = self.launch_configs["params"]
            run_results = []
            for c in configs:
                run_result = self.run(exec_path, problem_size_int=ps_int, **c)
                run_results.append(run_result)
                if self.display_runs:
                    logging.debug(run_result.stderr)
                    logging.debug(run_result.stdout)
                if self.early_exit_runs and (run_result.exit_code != 0 or not run_result.is_valid):
                    break

        return GeneratedTextResult(write_success, build_result, run_results)
