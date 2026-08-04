#!/usr/bin/env python3
"""charm4py benchmark driver for 07_fft_fft_conjugate"""
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
        x[k]         = even[k] + t
        x[k + N // 2] = even[k] - t
    # conjugate each element
    for i in range(N):
        x[i] = x[i].conjugate()


def correct_fn(x):
    _fft_cooley_tukey(x)


def validate(gen_fn):
    for _ in range(MAX_VALIDATION_ATTEMPTS):
        data = [complex(random.uniform(-1.0, 1.0), random.uniform(-1.0, 1.0)) for _ in range(1024)]
        ref = data.copy()
        correct_fn(ref)
        tst = data.copy()
        gen_fn(tst)
        if not all(abs(a - b) < 1e-3 for a, b in zip(ref, tst)):
            return False
    return True


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", required=True)
    parser.add_argument("--niter", type=int, default=NITER)
    opts = parser.parse_args(args[1:])
    try:
        gen_fn = load_fn(opts.generated, "fftConjugate")
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
    t = 0.0
    for _ in range(opts.niter):
        d = data.copy(); t0 = time.perf_counter(); gen_fn(d); t += time.perf_counter() - t0
    print(f"Time: {t/opts.niter:.6f}", flush=True)
    tb = 0.0
    for _ in range(opts.niter):
        d = data.copy(); t0 = time.perf_counter(); correct_fn(d); tb += time.perf_counter() - t0
    print(f"BestSequential: {tb/opts.niter:.6f}", flush=True)
    charm.exit()


charm.start(main)
