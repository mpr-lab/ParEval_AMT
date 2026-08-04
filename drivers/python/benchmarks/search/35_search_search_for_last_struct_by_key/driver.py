#!/usr/bin/env python3
"""charm4py benchmark driver for 35_search_search_for_last_struct_by_key"""
import argparse
import importlib.util
import random
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


def correct_fn(books):
    for i in range(len(books) - 1, -1, -1):
        if books[i]["pages"] < 100:
            return i
    return len(books)


def make_books(n, force_short=True):
    pages = [random.randint(1, 1000) for _ in range(n)]
    if force_short:
        pages[random.randint(0, n // 4)] = 72
    return [{"title": "title", "pages": p} for p in pages]


def validate(gen_fn):
    for _ in range(MAX_VALIDATION_ATTEMPTS):
        books = make_books(1024)
        correct = correct_fn(books)
        test = gen_fn(books)
        if correct != test:
            return False
    return True


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", required=True)
    parser.add_argument("--niter", type=int, default=NITER)
    opts = parser.parse_args(args[1:])
    try:
        gen_fn = load_fn(opts.generated, "findLastShortBook")
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
    books = make_books(PROBLEM_SIZE)
    t = 0.0
    for _ in range(opts.niter):
        t0 = time.perf_counter(); gen_fn(books); t += time.perf_counter() - t0
    print(f"Time: {t/opts.niter:.6f}", flush=True)
    tb = 0.0
    for _ in range(opts.niter):
        t0 = time.perf_counter(); correct_fn(books); tb += time.perf_counter() - t0
    print(f"BestSequential: {tb/opts.niter:.6f}", flush=True)
    charm.exit()


charm.start(main)
