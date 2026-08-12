""" Wrapper for calling Chapel drivers
    author: Adapted from Daniel Nichols' C++ driver
    date: June 2025
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

""" Map parallelism models to driver files """
DRIVER_MAP = {
    "serial": "serial-driver.chpl",
    "omp": "omp-driver.chpl",
    "mpi": "mpi-driver.chpl",
    "mpi+omp": "mpi-omp-driver.chpl",
}

""" Compiler settings for Chapel """
COMPILER_SETTINGS = {
    "serial": {"CHPL": "chpl", "CHPLFLAGS": "--fast"},
    "omp": {"CHPL": "chpl", "CHPLFLAGS": "--fast"},
    "mpi": {"CHPL": "chpl", "CHPLFLAGS": "--fast"},
    "mpi+omp": {"CHPL": "chpl", "CHPLFLAGS": "--fast"},
}

""" Chapel parallel validation """
from chapel.parallel_validation import ChapelOMPValidator, ChapelMPIValidator, ChapelMPIandOMPValidator, ChapelEmptyValidator

CHAPEL_VALIDATORS = {
    "serial": ChapelEmptyValidator(),
    "omp": ChapelOMPValidator(),
    "mpi": ChapelMPIValidator(),
    "mpi+omp": ChapelMPIandOMPValidator(),
}

class ChapelDriverWrapper(DriverWrapper):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Use Chapel-specific compiler settings
        if self.build_configs is None:
            self.build_configs = COMPILER_SETTINGS
        
        # Set Chapel-specific validator
        self.validator = CHAPEL_VALIDATORS.get(self.parallelism_model, ChapelEmptyValidator())
        
        self.model_driver_file = os.path.join("chapel", "models", DRIVER_MAP[self.parallelism_model])

    def write_source(self, content: str, fpath: PathLike) -> bool:
        """ Write the given Chapel source to the given file. """
        with open(fpath, "w") as fp:
            fp.write(content)
        return True

    def patch_prompt(self, content: str) -> str:
        """ Add NO_INLINE equivalent to the given source code. 
        In Chapel, we can add the 'noinline' attribute. """
        # For Chapel, we might need to patch the function signature
        # This is a placeholder - may need adjustment based on actual Chapel syntax
        return content

    def compile(
        self, 
        *binaries: PathLike, 
        output_path: PathLike = "a.out", 
        CHPL: str = "chpl", 
        CHPLFLAGS: str = "--fast",
        problem_size: str = "(1<<20)"
    ) -> BuildOutput:
        """ Compile the given Chapel source files into a single executable. """
        binaries_str = ' '.join(binaries)
        
        # Add appropriate flags based on parallelism model
        if self.parallelism_model == "mpi":
            macro = ""
        elif self.parallelism_model == "omp":
            macro = ""
        elif self.parallelism_model == "mpi+omp":
            macro = ""
        else:
            macro = ""
            
        # Chapel compiles source directly to executable
        cmd = f"{CHPL} {CHPLFLAGS} {macro} {binaries_str} -o {output_path}"
        
        try:
            compile_process = run_command(cmd, timeout=self.build_timeout, dry=self.dry)
        except subprocess.TimeoutExpired as e:
            return BuildOutput(-1, str(e.stdout), f"[Timeout] {str(e.stderr)}")
        
        return BuildOutput(compile_process.returncode, compile_process.stdout, compile_process.stderr)

    def run(self, executable: PathLike, **run_config) -> RunOutput:
        """ Run the given executable. """
        launch_format = self.launch_configs["format"]
        launch_cmd = launch_format.format(exec_path=executable, args="", **run_config).strip()
        try:
            run_process = run_command(launch_cmd, timeout=self.run_timeout, dry=self.dry)
        except subprocess.TimeoutExpired as e:
            return RunOutput(-1, str(e.stdout), f"[Timeout] {str(e.stderr)}", config=run_config)
        except UnicodeDecodeError as e:
            logging.warning(f"UnicodeDecodeError: {str(e)}\nRunning command: {launch_cmd}")
            return RunOutput(-1, "", f"UnicodeDecodeError: {str(e)}", config=run_config)
        return RunOutput(run_process.returncode, run_process.stdout, run_process.stderr, config=run_config)

    def test_single_output(self, prompt: str, output: str, test_driver_file: PathLike, problem_size: str) -> GeneratedTextResult:
        """ Test a single generated output. """
        logging.debug(f"Testing output:\n{output}")
        with tempfile.TemporaryDirectory(dir=self.scratch_dir) as tmpdir:
            # write out the prompt + output
            src_ext = "chpl"
            src_path = os.path.join(tmpdir, f"generated-code.{src_ext}")
            prompt = self.patch_prompt(prompt)
            write_success = self.write_source(prompt+"\n"+output, src_path)
            logging.debug(f"Wrote source to {src_path}.")

            # compile and run the output
            exec_path = os.path.join(tmpdir, "a.out")
            compiler_kwargs = copy.deepcopy(self.build_configs[self.parallelism_model])
            compiler_kwargs["problem_size"] = problem_size
            compiler_kwargs["CHPLFLAGS"] += f" -sDRIVER_PROBLEM_SIZE={problem_size}"
            
            build_result = self.compile(self.model_driver_file, test_driver_file, output_path=exec_path, **compiler_kwargs)
            logging.debug(f"Build result: {build_result}")
            if self.display_build_errors and build_result.stderr and not build_result.did_build:
                logging.debug(build_result.stderr)

            # run the code
            configs = self.launch_configs["params"]
            if build_result.did_build:
                run_results = []
                for c in configs:
                    run_result = self.run(exec_path, **c)
                    run_results.append(run_result)
                    if self.display_runs:
                        logging.debug(run_result.stderr)
                        logging.debug(run_result.stdout)
                    if self.early_exit_runs and (run_result.exit_code != 0 or not run_result.is_valid):
                        break
            else:
                run_results = None
            logging.debug(f"Run result: {run_results}")
            if run_results:
                for run_result in run_results:
                    if run_result.exit_code != 0:
                        logging.debug(f"Outputs:\n\tstdout: {run_result.stdout}\n\tstderr: {run_result.stderr}")
        
        return GeneratedTextResult(write_success, build_result, run_results)
