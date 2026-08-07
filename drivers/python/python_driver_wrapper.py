""" Wrapper for calling Python drivers (charm4py and serial).
    Mirrors CppDriverWrapper but replaces compile with an AST syntax-check
    and run with a direct python subprocess invocation.
"""
import ast
import copy
import logging
import os
from os import PathLike
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile

sys.path.append("..")
from drivers.driver_wrapper import DriverWrapper, BuildOutput, RunOutput, GeneratedTextResult
from util import run_command

DRIVER_MAP = {
    "charm4py": "driver.py",
    "serial": "driver.py",
}

LAUNCH_FORMAT = {
    "charm4py": "charmrun +p{num_pes} {driver_path} --generated {generated_path}",
    "serial": "python {driver_path} --generated {generated_path}",
}


class PythonDriverWrapper(DriverWrapper):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        model = self.parallelism_model
        if model not in DRIVER_MAP:
            raise ValueError(f"Unsupported Python parallelism model: {model}")
        self.driver_filename = DRIVER_MAP[model]

    # ------------------------------------------------------------------
    # DriverWrapper abstract interface
    # ------------------------------------------------------------------

    def write_source(self, content: str, fpath: PathLike) -> bool:
        try:
            with open(fpath, "w") as fp:
                fp.write(content)
            return True
        except Exception as exc:
            logging.error("Failed to write source to %s: %s", fpath, exc)
            return False

    def compile(self, *source_files: PathLike, output_path: PathLike = "a.out", **kwargs) -> BuildOutput:
        """'Compile' step for Python: parse every source file with ast.parse().
        Returns BuildOutput with exit_code=0 if all files are syntactically valid."""
        for fpath in source_files:
            if not str(fpath).endswith(".py"):
                continue
            try:
                with open(fpath, "r") as fp:
                    source = fp.read()
                ast.parse(source)
            except SyntaxError as exc:
                msg = f"SyntaxError in {fpath}: {exc}"
                logging.debug(msg)
                return BuildOutput(1, "", msg)
            except Exception as exc:
                msg = f"Error reading {fpath}: {exc}"
                logging.error(msg)
                return BuildOutput(1, "", msg)
        # "output_path" is the path we'll store the generated .py at; no binary produced
        return BuildOutput(0, "", "")

    def run(self, executable: PathLike, **run_config) -> RunOutput:
        """Run the benchmark driver subprocess.

        `executable` here is the full shell command string built by
        test_single_output (e.g. 'charmrun +p4 .../charm4py.py --generated ...').
        """
        try:
            run_process = run_command(executable, timeout=self.run_timeout, dry=self.dry)
        except subprocess.TimeoutExpired as exc:
            return RunOutput(-1, str(exc.stdout or ""), f"[Timeout] {str(exc.stderr or '')}", config=run_config)
        except UnicodeDecodeError as exc:
            return RunOutput(-1, "", f"UnicodeDecodeError: {exc}", config=run_config)
        return RunOutput(run_process.returncode, run_process.stdout, run_process.stderr, config=run_config)

    def test_single_output(
        self,
        prompt: str,
        output: str,
        test_driver_file: PathLike,
        problem_size: str,
        problem_type: str,
    ) -> GeneratedTextResult:
        """Test a single generated Python output."""
        logging.debug("Testing output:\n%s", output)

        with tempfile.TemporaryDirectory(dir=self.scratch_dir) as tmpdir:
            # Write generated code to a temp .py file
            generated_path = os.path.join(tmpdir, "generated_code.py")
            write_success = self.write_source(output, generated_path)
            logging.debug("Wrote generated source to %s.", generated_path)

            # Syntax-check the generated file
            build_result = self.compile(generated_path)
            if self.display_build_errors and not build_result.did_build:
                logging.error("Syntax error in generated code: %s", build_result.stderr)

            if not build_result.did_build:
                return GeneratedTextResult(write_success, build_result, None)

            # Build the launch command for each config and run
            configs = self.launch_configs.get("params", [{}])
            run_results = []

            abs_driver = self._resolve_driver_path(test_driver_file, problem_type)
            fmt = self.launch_configs.get("format", "{driver_path} --generated {generated_path}")

            for c in configs:
                cmd = fmt.format(
                    driver_path=shlex.quote(abs_driver),
                    generated_path=shlex.quote(generated_path),
                    args="",
                    **c,
                )
                run_result = self.run(cmd.strip(), **c)
                run_results.append(run_result)
                if self.display_runs:
                    logging.debug("stdout: %s", run_result.stdout)
                    logging.debug("stderr: %s", run_result.stderr)
                if self.early_exit_runs and (run_result.exit_code != 0 or not run_result.is_valid):
                    break

        return GeneratedTextResult(write_success, build_result, run_results)

    def _resolve_driver_path(self, test_driver_file: PathLike, problem_type: str) -> str:
        """Resolve driver file path and recover from malformed relative inputs.

        Some datasets may contain stray whitespace in metadata, which can leak into
        relative paths and break process argument tokenization. This resolver strips
        surrounding whitespace and validates that we end at a concrete driver file.
        """
        raw = str(test_driver_file).strip()
        candidate = Path(raw)
        if not candidate.is_absolute():
            candidate = Path(os.getcwd()) / candidate
        candidate = candidate.resolve()
        if candidate.is_file():
            return str(candidate)

        # If caller accidentally passed a directory, try the expected filename.
        if candidate.is_dir():
            dir_candidate = (candidate / self.driver_filename).resolve()
            if dir_candidate.is_file():
                return str(dir_candidate)

        # Fallback: reconstruct from normalized python benchmark layout.
        cleaned_parts = [p for p in raw.replace("\r", "").replace("\n", "").split("/") if p]
        expected_problem = cleaned_parts[-2] if len(cleaned_parts) >= 2 else None
        if expected_problem:
            recovered = (
                Path(os.getcwd())
                / "python"
                / "benchmarks"
                / str(problem_type).strip()
                / expected_problem
                / self.driver_filename
            ).resolve()
            if recovered.is_file():
                return str(recovered)

        raise FileNotFoundError(
            f"Could not resolve python benchmark driver file from '{test_driver_file}'. "
            f"Resolved candidate was '{candidate}'."
        )
