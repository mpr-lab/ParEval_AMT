use Time, Random;
config const problemSize: int = 1 << 8;
const NITER = 5;

record COOElement { var row: int; var col: int; var value: real; }

proc correctSpmm(A: [] COOElement, X: [] COOElement, ref Y: [] real, M: int, K: int, N: int) {
  Y = 0.0;
  var Xd: [0..<K*N] real = 0.0;
  for e in X do Xd[e.row*N+e.col] += e.value;
  for ea in A do for j in 0..<N do Y[ea.row*N+j] += ea.value * Xd[ea.col*N+j];
}

proc doValidate(): bool {
  const m = 16; const k = 16; const n = 16; const nnz = 32;
  for trial in 0..1 {
    var A: [0..<nnz] COOElement; var X: [0..<nnz] COOElement;
    var rs = new randomStream(real, seed=trial+1);
    for i in A.domain { A[i].row=(rs.rand()*m):int%m; A[i].col=(rs.rand()*k):int%k; A[i].value=rs.rand()*2-1; }
    for i in X.domain { X[i].row=(rs.rand()*k):int%k; X[i].col=(rs.rand()*n):int%n; X[i].value=rs.rand()*2-1; }
    var Yc, Yt: [0..<m*n] real;
    correctSpmm(A, X, Yc, m, k, n);
    spmm(A, X, Yt, m, k, n);
    for i in Yc.domain do if abs(Yc[i]-Yt[i]) > 1e-8 then return false;
  }
  return true;
}

proc main() {
  const M = problemSize; const K = problemSize; const N = problemSize;
  const nnz = M * K / 5;
  var A: [0..<nnz] COOElement; var X: [0..<nnz] COOElement; var Y: [0..<M*N] real;
  var rs = new randomStream(real, seed=42);
  for i in A.domain { A[i].row=(rs.rand()*M):int%M; A[i].col=(rs.rand()*K):int%K; A[i].value=rs.rand()*2-1; }
  for i in X.domain { X[i].row=(rs.rand()*K):int%K; X[i].col=(rs.rand()*N):int%N; X[i].value=rs.rand()*2-1; }

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for i in 0..<NITER { Y = 0.0; sw.restart(); spmm(A, X, Y, M, K, N); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for i in 0..<NITER { Y = 0.0; sw.restart(); correctSpmm(A, X, Y, M, K, N); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}
