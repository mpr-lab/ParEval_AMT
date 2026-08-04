#!/usr/bin/env python3
"""charm4py benchmark driver for 16_graph_largest_component"""
import argparse
import importlib.util
import random
import time
from charm4py import charm

N_BENCH = 1024
N_VAL = 64
NITER = 5
MAX_VALIDATION_ATTEMPTS = 2


def load_fn(path, fn_name):
    spec = importlib.util.spec_from_file_location("generated", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, fn_name)


def rand_undirected_graph(N):
    A = [0] * (N * N)
    for i in range(N):
        for j in range(i + 1, N):
            v = random.randint(0, 1)
            A[i * N + j] = v
            A[j * N + i] = v
    return A


def correct_largest_component(A, N):
    visited = [False] * N

    def dfs(node):
        stack = [node]
        count = 0
        while stack:
            n = stack.pop()
            if visited[n]:
                continue
            visited[n] = True
            count += 1
            for i in range(N):
                if A[n * N + i] == 1 and not visited[i]:
                    stack.append(i)
        return count

    max_count = 0
    for i in range(N):
        if not visited[i]:
            max_count = max(max_count, dfs(i))
    return max_count


def validate(gen_fn):
    for _ in range(MAX_VALIDATION_ATTEMPTS):
        A = rand_undirected_graph(N_VAL)
        expected = correct_largest_component(A, N_VAL)
        result = gen_fn(A, N_VAL)
        if result != expected:
            return False
    return True


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", required=True)
    parser.add_argument("--niter", type=int, default=NITER)
    opts = parser.parse_args(args[1:])
    try:
        gen_fn = load_fn(opts.generated, "largestComponent")
    except Exception:
        print("Validation: FAIL"); charm.exit(); return
    is_valid = validate(gen_fn)
    print(f"Validation: {'PASS' if is_valid else 'FAIL'}", flush=True)
    if not is_valid:
        charm.exit(); return
    A = rand_undirected_graph(N_BENCH)
    t = 0.0
    for _ in range(opts.niter):
        t0 = time.perf_counter(); gen_fn(A, N_BENCH); t += time.perf_counter() - t0
    print(f"Time: {t/opts.niter:.6f}", flush=True)
    tb = 0.0
    for _ in range(opts.niter):
        t0 = time.perf_counter(); correct_largest_component(A, N_BENCH); tb += time.perf_counter() - t0
    print(f"BestSequential: {tb/opts.niter:.6f}", flush=True)
    charm.exit()


charm.start(main)
