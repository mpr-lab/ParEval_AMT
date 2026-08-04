#!/usr/bin/env python3
"""charm4py benchmark driver for 23_histogram_first_letter_counts"""
import argparse
import importlib.util
import random
import string
import time
from charm4py import charm

PROBLEM_SIZE = 1 << 20
NITER = 5
MAX_VALIDATION_ATTEMPTS = 2


def load_fn(path, fn_name):
    spec = importlib.util.spec_from_file_location("generated", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, fn_name)


def rand_strings(n, min_len=2, max_len=10):
    result = []
    for _ in range(n):
        length = random.randint(min_len, max_len)
        s = ''.join(random.choices(string.ascii_lowercase, k=length))
        result.append(s)
    return result


def correct_fn(s, bins):
    for word in s:
        bins[ord(word[0]) - ord('a')] += 1


def validate(gen_fn):
    for _ in range(MAX_VALIDATION_ATTEMPTS):
        s = rand_strings(1024)
        correct = [0] * 26
        correct_fn(s, correct)
        test = [0] * 26
        gen_fn(s, test)
        if correct != test:
            return False
    return True


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", required=True)
    parser.add_argument("--niter", type=int, default=NITER)
    opts = parser.parse_args(args[1:])
    try:
        gen_fn = load_fn(opts.generated, "firstLetterCounts")
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
    s = rand_strings(PROBLEM_SIZE)
    t = 0.0
    for _ in range(opts.niter):
        bins = [0] * 26
        t0 = time.perf_counter(); gen_fn(s, bins); t += time.perf_counter() - t0
    print(f"Time: {t/opts.niter:.6f}", flush=True)
    tb = 0.0
    for _ in range(opts.niter):
        bins = [0] * 26
        t0 = time.perf_counter(); correct_fn(s, bins); tb += time.perf_counter() - t0
    print(f"BestSequential: {tb/opts.niter:.6f}", flush=True)
    charm.exit()


charm.start(main)
