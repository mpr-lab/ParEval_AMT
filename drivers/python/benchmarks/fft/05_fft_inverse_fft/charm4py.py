#!/usr/bin/env python3
"""charm4py benchmark driver for 05_fft_inverse_fft"""
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


def _fft_inplace(x):
    N = len(x)
    k = N
    theta_t = math.pi / N
    phi_t = complex(math.cos(theta_t), -math.sin(theta_t))
    while k > 1:
        n = k
        k >>= 1
        phi_t = phi_t * phi_t
        T = 1.0
        for l in range(k):
            a = l
            while a < N:
                b = a + k
                t = x[a] - x[b]
                x[a] += x[b]
                x[b] = t * T
                a += n
            T *= phi_t
    m = int(math.log2(N))
    for a in range(N):
        b = a
        b = (((b & 0xaaaaaaaa) >> 1) | ((b & 0x55555555) << 1))
        b = (((b & 0xcccccccc) >> 2) | ((b & 0x33333333) << 2))
        b = (((b & 0xf0f0f0f0) >> 4) | ((b & 0x0f0f0f0f) << 4))
        b = (((b & 0xff00ff00) >> 8) | ((b & 0x00ff00ff) << 8))
        b = ((b >> 16) | (b << 16)) >> (32 - m)
        if b > a:
            x[a], x[b] = x[b], x[a]


def correct_fn(x):
    # conjugate
    for i in range(len(x)):
        x[i] = x[i].conjugate()
    # forward fft
    _fft_inplace(x)
    # conjugate again and scale
    n = len(x)
    for i in range(n):
        x[i] = x[i].conjugate() / n


def validate(gen_fn):
    for _ in range(MAX_VALIDATION_ATTEMPTS):
        data = [complex(random.uniform(-1.0, 1.0), random.uniform(-1.0, 1.0)) for _ in range(1024)]
        ref = data.copy()
        correct_fn(ref)
        tst = data.copy()
        gen_fn(tst)
        if not all(abs(a - b) < 1e-4 for a, b in zip(ref, tst)):
            return False
    return True


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", required=True)
    parser.add_argument("--niter", type=int, default=NITER)
    opts = parser.parse_args(args[1:])
    try:
        gen_fn = load_fn(opts.generated, "ifft")
    except Exception as e:
        print("Validation: FAIL"); charm.exit(); return
    is_valid = validate(gen_fn)
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
