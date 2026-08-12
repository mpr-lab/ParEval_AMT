use Time, Random;
config const problemSize: int = 1 << 11;
const NITER = 5;

record COOElement { var row: int; var col: int; var value: real; }

proc correctSpmv(alpha: real, A: [] COOElement, x: [] real, beta: real, ref y: [] real, M: int, N: int) {
  for i in y.domain do y[i] *= beta;
  for e in A do y[e.row] += alpha * e.value * x[e.col];
}

proc doValidate(): bool {
  const m = 64; const n = 64; const nnz = 256;
  for trial in 0..1 {
    var A: [0..<nnz] COOElement; var x: [0..<n] real; var yc, yt: [0..<m] real;
    var rs = new randomStream(real, seed=trial+1);
    for i in A.domain { A[i].row = (rs.next()*m):int % m; A[i].col = (rs.next()*n):int % n; A[i].value = rs.next()*2-1; }
    rs.fill(x); rs.fill(yc); yt = yc;
    const alpha = 0.5; const beta = 1.0;
    correctSpmv(alpha, A, x, beta, yc, m, n);
    spmv(alpha, A, x, beta, yt, m, n);
    for i in yc.domain do if abs(yc[i]-yt[i]) > 1e-8 then return false;
  }
  return true;
}

proc main() {
  const M = problemSize; const N = problemSize;
  const nnz = (M * N):int / 10;
  var A: [0..<nnz] COOElement; var x: [0..<N] real; var y: [0..<M] real;
  var rs = new randomStream(real, seed=42);
  for i in A.domain { A[i].row = (rs.next()*M):int % M; A[i].col = (rs.next()*N):int % N; A[i].value = rs.next()*2-1; }
  rs.fill(x); rs.fill(y);
  const alpha = 0.5; const beta = 1.0;
  const origY = y;

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for i in 0..<NITER { y = origY; sw.restart(); spmv(alpha, A, x, beta, y, M, N); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for i in 0..<NITER { y = origY; sw.restart(); correctSpmv(alpha, A, x, beta, y, M, N); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}
