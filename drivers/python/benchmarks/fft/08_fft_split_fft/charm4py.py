#!/usr/bin/env python3
"""charm4py benchmark driver for 08_fft_split_fft"""
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


def correct_fn(x, r, i):
    tmp = x.copy()
    _fft_cooley_tukey(tmp)
    for j in range(len(tmp)):
        r[j] = tmp[j].real
        i[j] = tmp[j].imag


def validate(gen_fn):
    size = 1024
    for _ in range(MAX_VALIDATION_ATTEMPTS):
        data = [complex(random.uniform(-1.0, 1.0), random.uniform(-1.0, 1.0)) for _ in range(size)]
        ref_r = [0.0] * size
        ref_i = [0.0] * size
        correct_fn(data, ref_r, ref_i)
        tst_r = [0.0] * size
        tst_i = [0.0] * size
        gen_fn(data, tst_r, tst_i)
        if not (all(abs(a - b) < 1e-4 for a, b in zip(ref_r, tst_r)) and
                all(abs(a - b) < 1e-4 for a, b in zip(ref_i, tst_i))):
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
    is_valid = validate(gen_fn)
    print(f"Validation: {'PASS' if is_valid else 'FAIL'}", flush=True)
    if not is_valid:
        charm.exit(); return
    data = [complex(random.uniform(-1.0, 1.0), random.uniform(-1.0, 1.0)) for _ in range(PROBLEM_SIZE)]
    r_out = [0.0] * PROBLEM_SIZE
    i_out = [0.0] * PROBLEM_SIZE
    t = 0.0
    for _ in range(opts.niter):
        r = r_out.copy(); i = i_out.copy()
        t0 = time.perf_counter(); gen_fn(data, r, i); t += time.perf_counter() - t0
    print(f"Time: {t/opts.niter:.6f}", flush=True)
    tb = 0.0
    for _ in range(opts.niter):
        r = r_out.copy(); i = i_out.copy()
        t0 = time.perf_counter(); correct_fn(data, r, i); tb += time.perf_counter() - t0
    print(f"BestSequential: {tb/opts.niter:.6f}", flush=True)
    charm.exit()


charm.start(main)
