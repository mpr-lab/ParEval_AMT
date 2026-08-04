#!/usr/bin/env python3
"""charm4py benchmark driver for 48_sparse_la_sparse_axpy"""
import argparse
import importlib.util
import random
import time
from charm4py import charm

# Problem 48 uses sparse *vectors* (not matrices).
# N is the vector length; nVals = N * SPARSITY elements.
N_BENCH = 256
N_VAL = 16
SPARSITY = 0.1
NITER = 5
MAX_VALIDATION_ATTEMPTS = 2


def load_fn(path, fn_name):
    spec = importlib.util.spec_from_file_location("generated", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, fn_name)


def make_sparse_vector(N, sparsity):
    """Generate a sorted sparse vector as list of dicts with 'index' and 'value'."""
    n_vals = max(1, int(N * sparsity))
    indices = sorted(random.sample(range(N), min(n_vals, N)))
    return [{'index': idx, 'value': random.uniform(-1.0, 1.0)} for idx in indices]


def correct_sparse_axpy(alpha, x, y, N):
    """Compute z = alpha*x + y for sparse vectors x and y; result is a dense vector."""
    z = [0.0] * N
    xi, yi = 0, 0
    while xi < len(x) and yi < len(y):
        if x[xi]['index'] < y[yi]['index']:
            z[x[xi]['index']] += alpha * x[xi]['value']
            xi += 1
        elif x[xi]['index'] > y[yi]['index']:
            z[y[yi]['index']] += y[yi]['value']
            yi += 1
        else:
            z[x[xi]['index']] += alpha * x[xi]['value'] + y[yi]['value']
            xi += 1
            yi += 1
    while xi < len(x):
        z[x[xi]['index']] += alpha * x[xi]['value']
        xi += 1
    while yi < len(y):
        z[y[yi]['index']] += y[yi]['value']
        yi += 1
    return z


def validate(gen_fn):
    for _ in range(MAX_VALIDATION_ATTEMPTS):
        N = N_VAL
        alpha = random.uniform(-1.0, 1.0)
        x = make_sparse_vector(N, SPARSITY)
        y = make_sparse_vector(N, SPARSITY)
        z_ref = correct_sparse_axpy(alpha, x, y, N)
        z_test = [0.0] * N
        gen_fn(alpha, x, y, z_test)
        if not all(abs(a - b) < 1e-4 for a, b in zip(z_ref, z_test)):
            return False
    return True


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", required=True)
    parser.add_argument("--niter", type=int, default=NITER)
    opts = parser.parse_args(args[1:])

    try:
        gen_fn = load_fn(opts.generated, "sparseAxpy")
    except Exception:
        print("Validation: FAIL"); charm.exit(); return

    is_valid = validate(gen_fn)
    print(f"Validation: {'PASS' if is_valid else 'FAIL'}", flush=True)
    if not is_valid:
        charm.exit(); return

    N = N_BENCH
    alpha = random.uniform(-1.0, 1.0)
    x = make_sparse_vector(N, SPARSITY)
    y = make_sparse_vector(N, SPARSITY)

    t = 0.0
    for _ in range(opts.niter):
        z = [0.0] * N
        t0 = time.perf_counter()
        gen_fn(alpha, x, y, z)
        t += time.perf_counter() - t0
    print(f"Time: {t/opts.niter:.6f}", flush=True)

    tb = 0.0
    for _ in range(opts.niter):
        t0 = time.perf_counter()
        correct_sparse_axpy(alpha, x, y, N)
        tb += time.perf_counter() - t0
    print(f"BestSequential: {tb/opts.niter:.6f}", flush=True)
    charm.exit()


charm.start(main)
