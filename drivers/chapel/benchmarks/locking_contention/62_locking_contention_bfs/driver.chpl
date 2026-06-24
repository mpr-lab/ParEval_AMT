use Time, Random;
config const problemSize: int = 1 << 12;
const NITER = 5;

proc correctBfs(A: [] int, N: int, source: int, ref dist: [] int) {
  dist = -1; dist[source] = 0;
  var queue: [0..<N] int; var head = 0; var tail = 0;
  queue[tail] = source; tail += 1;
  while head < tail { const u = queue[head]; head += 1;
    for v in 0..<N do if A[u*N+v] != 0 && dist[v] == -1 { dist[v] = dist[u]+1; queue[tail] = v; tail += 1; } }
}

proc doValidate(): bool {
  const n = 64;
  for trial in 0..1 {
    var A: [0..<n*n] int; var rs = new randomStream(int, seed=trial+1); rs.fill(A);
    for i in 0..<n do for j in 0..<n { A[i*n+j] = abs(A[i*n+j])%2; A[j*n+i] = A[i*n+j]; A[i*n+i] = 0; }
    var dc, dt: [0..<n] int;
    correctBfs(A, n, 0, dc); bfs(A, n, 0, dt);
    for i in dc.domain do if dc[i] != dt[i] then return false;
  }
  return true;
}

proc main() {
  const N = problemSize; var A: [0..<N*N] int; var rs = new randomStream(int, seed=42); rs.fill(A);
  for i in 0..<N do for j in 0..<N { A[i*N+j] = abs(A[i*N+j])%2; A[j*N+i] = A[i*N+j]; A[i*N+i] = 0; }
  var dist: [0..<N] int;

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch; var computeTotal = 0.0;
  for i in 0..<NITER { sw.restart(); bfs(A, N, 0, dist); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);
  var bestTotal = 0.0;
  for i in 0..<NITER { sw.restart(); correctBfs(A, N, 0, dist); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}
