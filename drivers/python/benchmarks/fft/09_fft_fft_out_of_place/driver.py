#!/usr/bin/env python3
"""charm4py benchmark driver for 09_fft_fft_out_of_place"""
import argparse, importlib.util, random, cmath, time, math
from charm4py import charm

PROBLEM_SIZE = 1 << 20
NITER = 5
MAX_VALIDATION_ATTEMPTS = 2


def load_fn(path, fn_name):
    spec = importlib.util.spec_from_file_location("generated", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, fn_name)


def _fft_cooley_tukey(x):
    N = len(x)
    if N <= 1:
        return
    even = [x[i * 2] for i in range(N // 2)]
    odd  = [x[i * 2 + 1] for i in range(N // 2)]
    _fft_cooley_tukey(even)
    _fft_cooley_tukey(odd)
    for k in range(N // 2):
        t = cmath.rect(1.0, -2 * math.pi * k / N) * odd[k]
        x[k]          = even[k] + t
        x[k + N // 2] = even[k] - t


def correct_fn(x, output):
    tmp = list(x)
    _fft_cooley_tukey(tmp)
    for j in range(len(tmp)):
        output[j] = tmp[j]


def validate(gen_fn):
    size = 1024
    for _ in range(MAX_VALIDATION_ATTEMPTS):
        data = [complex(random.uniform(-1.0, 1.0), random.uniform(-1.0, 1.0)) for _ in range(size)]
        ref = [0j] * size
        correct_fn(data, ref)
        tst = [0j] * size
        gen_fn(data, tst)
        if not all(abs(a - b) < 1e-4 for a, b in zip(ref, tst)):
            return False
    return True


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", required=True)
    parser.add_argument("--niter", type=int, default=NITER)
    opts = parser.parse_args(args[1:])
    try:
        gen_fn = load_fn(opts.generated, "fft")
    except Exception as e:
        print("Validation: FAIL"); charm.exit(); return
    try:
        is_valid = validate(gen_fn)
    except Exception as _ve:
        print(f"Validation: FAIL")
        print(f"Runtime error: {_ve}", flush=True)
        charm.exit()
        return
    print(f"Validation: {'PASS' if is_valid else 'FAIL'}", flush=True)
    if not is_valid:
        charm.exit(); return
    data = [complex(random.uniform(-1.0, 1.0), random.uniform(-1.0, 1.0)) for _ in range(PROBLEM_SIZE)]
    output = [0j] * PROBLEM_SIZE
    t = 0.0
    for _ in range(opts.niter):
        out = output.copy(); t0 = time.perf_counter(); gen_fn(data, out); t += time.perf_counter() - t0
    print(f"Time: {t/opts.niter:.6f}", flush=True)
    tb = 0.0
    for _ in range(opts.niter):
        out = output.copy(); t0 = time.perf_counter(); correct_fn(data, out); tb += time.perf_counter() - t0
    print(f"BestSequential: {tb/opts.niter:.6f}", flush=True)
    charm.exit()


charm.start(main)
