#!/usr/bin/env python3
"""charm4py benchmark driver for 54_stencil_game_of_life"""
import argparse
import importlib.util
import random
import time
from charm4py import charm

N_BENCH = 512
N_VAL = 32
NITER = 5
MAX_VALIDATION_ATTEMPTS = 2


def load_fn(path, fn_name):
    spec = importlib.util.spec_from_file_location("generated", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, fn_name)


def correct_fn(inp, out, N):
    for i in range(N):
        for j in range(N):
            s = 0
            if i > 0:
                s += inp[(i - 1) * N + j]
            if i < N - 1:
                s += inp[(i + 1) * N + j]
            if j > 0:
                s += inp[i * N + j - 1]
            if j < N - 1:
                s += inp[i * N + j + 1]
            if i > 0 and j > 0:
                s += inp[(i - 1) * N + j - 1]
            if i > 0 and j < N - 1:
                s += inp[(i - 1) * N + j + 1]
            if i < N - 1 and j > 0:
                s += inp[(i + 1) * N + j - 1]
            if i < N - 1 and j < N - 1:
                s += inp[(i + 1) * N + j + 1]
            if inp[i * N + j] == 1:
                out[i * N + j] = 1 if s in (2, 3) else 0
            else:
                out[i * N + j] = 1 if s == 3 else 0


def validate(gen_fn):
    for _ in range(MAX_VALIDATION_ATTEMPTS):
        N = N_VAL
        inp = [random.randint(0, 1) for _ in range(N * N)]
        ref = [0] * (N * N)
        correct_fn(inp, ref, N)
        tst = [0] * (N * N)
        gen_fn(inp, tst, N)
        for i in range(1, N - 1):
            for j in range(1, N - 1):
                if tst[i * N + j] != ref[i * N + j]:
                    return False
    return True


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", required=True)
    parser.add_argument("--niter", type=int, default=NITER)
    opts = parser.parse_args(args[1:])
    try:
        gen_fn = load_fn(opts.generated, "gameOfLife")
    except Exception:
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

    N = N_BENCH
    inp = [random.randint(0, 1) for _ in range(N * N)]
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
