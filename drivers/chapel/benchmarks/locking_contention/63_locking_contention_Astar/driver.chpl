use Time, Random, Math;
config const problemSize: int = 1 << 12;
const NITER = 5;

proc heuristic(u: int, dest: int, N: int): int {
  const ur = u / N; const uc = u % N;
  const dr = dest / N; const dc = dest % N;
  return abs(ur-dr) + abs(uc-dc);
}

proc correctAstar(A: [] int, N: int, source: int, dest: int): int {
  var dist: [0..<N] int = max(int);
  dist[source] = 0;
  var visited: [0..<N] bool = false;
  for _ in 0..<N {
    var u = -1;
    for v in 0..<N do if !visited[v] && dist[v] != max(int) do if u == -1 || dist[v]+heuristic(v,dest,N) < dist[u]+heuristic(u,dest,N) then u = v;
    if u == -1 || u == dest then break;
    visited[u] = true;
    for v in 0..<N do if A[u*N+v] != 0 && dist[u]+1 < dist[v] then dist[v] = dist[u]+1;
  }
  return if dist[dest] == max(int) then -1 else dist[dest];
}

proc doValidate(): bool {
  const n = 32;
  for trial in 0..1 {
    var A: [0..<n*n] int; var rs = new randomStream(int, seed=trial+1); rs.fill(A);
    for i in 0..<n do for j in 0..<n { A[i*n+j] = abs(A[i*n+j])%2; A[j*n+i] = A[i*n+j]; A[i*n+i] = 0; }
    if correctAstar(A, n, 0, n-1) != astar(A, n, 0, n-1) then return false;
  }
  return true;
}

proc main() {
  const N = problemSize; var A: [0..<N*N] int; var rs = new randomStream(int, seed=42); rs.fill(A);
  for i in 0..<N do for j in 0..<N { A[i*N+j] = abs(A[i*N+j])%2; A[j*N+i] = A[i*N+j]; A[i*N+i] = 0; }

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch; var computeTotal = 0.0;
  for i in 0..<NITER { sw.restart(); var r = astar(A, N, 0, N-1); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);
  var bestTotal = 0.0;
  for i in 0..<NITER { sw.restart(); var r = correctAstar(A, N, 0, N-1); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}
