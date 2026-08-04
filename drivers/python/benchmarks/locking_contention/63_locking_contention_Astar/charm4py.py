#!/usr/bin/env python3
"""charm4py benchmark driver for 63_locking_contention_Astar"""
import argparse, importlib.util, random, time, heapq, math
from charm4py import charm

PROBLEM_SIZE = 512
NITER = 3
MAX_VALIDATION_ATTEMPTS = 2


def load_fn(path, fn_name):
    spec = importlib.util.spec_from_file_location("generated", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, fn_name)


def build_weighted_grid(rows, cols, rng=None):
    """Build weighted grid graph and Manhattan-distance heuristic toward goal=(rows*cols-1).

    Returns (graph, heuristic) where:
      graph: list of lists of (neighbor, cost) tuples
      heuristic: list of floats (Manhattan distance to goal)
    """
    if rng is None:
        rng = random.Random(42)
    n = rows * cols
    graph = [[] for _ in range(n)]
    goal = n - 1
    goal_r, goal_c = goal // cols, goal % cols

    for r in range(rows):
        for c in range(cols):
            u = r * cols + c
            if c + 1 < cols:
                v = r * cols + (c + 1)
                cost = rng.uniform(0.5, 5.0)
                graph[u].append((v, cost))
                graph[v].append((u, cost))
            if r + 1 < rows:
                v = (r + 1) * cols + c
                cost = rng.uniform(0.5, 5.0)
                graph[u].append((v, cost))
                graph[v].append((u, cost))

    heuristic = []
    for node in range(n):
        nr, nc = node // cols, node % cols
        heuristic.append(float(abs(goal_r - nr) + abs(goal_c - nc)))

    return graph, heuristic


def correct_fn(graph, start, goal, heuristic):
    """A* search returning {'found': bool, 'path': list, 'total_cost': float}."""
    n = len(graph)
    if start >= n or goal >= n:
        return {'found': False, 'path': [], 'total_cost': float('inf')}

    INF = float('inf')
    g_score = [INF] * n
    g_score[start] = 0.0
    parent = [-1] * n
    parent[start] = start
    closed = [False] * n

    # heap: (f, node)
    heap = [(heuristic[start], start)]

    while heap:
        f, u = heapq.heappop(heap)
        if closed[u]:
            continue
        closed[u] = True
        if u == goal:
            break
        g_u = g_score[u]
        for v, cost in graph[u]:
            if closed[v]:
                continue
            tentative_g = g_u + cost
            if tentative_g + 1e-12 < g_score[v]:
                g_score[v] = tentative_g
                parent[v] = u
                heapq.heappush(heap, (tentative_g + heuristic[v], v))

    if not closed[goal]:
        return {'found': False, 'path': [], 'total_cost': float('inf')}

    path = []
    node = goal
    while node != start:
        path.append(node)
        node = parent[node]
    path.append(start)
    path.reverse()

    return {'found': True, 'path': path, 'total_cost': g_score[goal]}


def path_cost(graph, path):
    if len(path) < 2:
        return 0.0
    total = 0.0
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        found = False
        for nb, cost in graph[u]:
            if nb == v:
                total += cost
                found = True
                break
        if not found:
            return float('inf')
    return total


def validate(gen_fn):
    base_dim = 8
    for attempt in range(MAX_VALIDATION_ATTEMPTS):
        dim = base_dim + attempt
        rng = random.Random(42 + attempt)
        graph, heuristic = build_weighted_grid(dim, dim, rng)
        start = 0
        goal = dim * dim - 1
        expected = correct_fn(graph, start, goal, heuristic)
        try:
            result = gen_fn(graph, start, goal, heuristic)
        except Exception:
            return False
        if expected['found'] != result.get('found', False):
            return False
        if expected['found']:
            ref_cost = path_cost(graph, expected['path'])
            trial_cost = path_cost(graph, result.get('path', []))
            if abs(ref_cost - trial_cost) > 1e-5:
                return False
    return True


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", required=True)
    parser.add_argument("--niter", type=int, default=NITER)
    opts = parser.parse_args(args[1:])

    try:
        gen_fn = load_fn(opts.generated, "parallel_astar")
    except Exception:
        print("Validation: FAIL"); charm.exit(); return

    is_valid = validate(gen_fn)
    print(f"Validation: {'PASS' if is_valid else 'FAIL'}", flush=True)
    if not is_valid:
        charm.exit(); return

    dim = max(4, int(math.sqrt(PROBLEM_SIZE)))
    graph, heuristic = build_weighted_grid(dim, dim)
    start = 0
    goal = dim * dim - 1

    t = 0.0
    for _ in range(opts.niter):
        t0 = time.perf_counter()
        gen_fn(graph, start, goal, heuristic)
        t += time.perf_counter() - t0
    print(f"Time: {t/opts.niter:.6f}", flush=True)

    tb = 0.0
    for _ in range(opts.niter):
        t0 = time.perf_counter()
        correct_fn(graph, start, goal, heuristic)
        tb += time.perf_counter() - t0
    print(f"BestSequential: {tb/opts.niter:.6f}", flush=True)

    charm.exit()


charm.start(main)
