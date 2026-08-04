#!/usr/bin/env python3
"""charm4py benchmark driver for 51_stencil_edge_kernel"""
import argparse
import importlib.util
import random
import time
from charm4py import charm

EDGE_KERNEL = [[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]]
N_BENCH = 512
N_VAL = 32
NITER = 5
MAX_VALIDATION_ATTEMPTS = 2


def load_fn(path, fn_name):
    spec = importlib.util.spec_from_file_location("generated", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, fn_name)


def correct_fn(image_in, image_out, N):
    for i in range(N):
        for j in range(N):
            s = 0
            for k in range(-1, 2):
                for l in range(-1, 2):
                    x, y = i + k, j + l
                    if 0 <= x < N and 0 <= y < N:
                        s += image_in[x * N + y] * EDGE_KERNEL[k + 1][l + 1]
            image_out[i * N + j] = max(0, min(255, s))


def validate(gen_fn):
    for _ in range(MAX_VALIDATION_ATTEMPTS):
        N = N_VAL
        inp = [random.randint(0, 255) for _ in range(N * N)]
        ref = [0] * (N * N)
        correct_fn(inp, ref, N)
        tst = [0] * (N * N)
        gen_fn(inp, tst, N)
        if ref != tst:
            return False
    return True


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", required=True)
    parser.add_argument("--niter", type=int, default=NITER)
    opts = parser.parse_args(args[1:])
    try:
        gen_fn = load_fn(opts.generated, "convolveKernel")
    except Exception:
        print("Validation: FAIL"); charm.exit(); return
    is_valid = validate(gen_fn)
    print(f"Validation: {'PASS' if is_valid else 'FAIL'}", flush=True)
    if not is_valid:
        charm.exit(); return

    N = N_BENCH
    inp = [random.randint(0, 255) for _ in range(N * N)]
    out = [0] * (N * N)
    t = 0.0
    for _ in range(opts.niter):
        o = out.copy(); t0 = time.perf_counter(); gen_fn(inp, o, N); t += time.perf_counter() - t0
    print(f"Time: {t/opts.niter:.6f}", flush=True)

    tb = 0.0
    for _ in range(opts.niter):
        o = out.copy(); t0 = time.perf_counter(); correct_fn(inp, o, N); tb += time.perf_counter() - t0
    print(f"BestSequential: {tb/opts.niter:.6f}", flush=True)
    charm.exit()


charm.start(main)
