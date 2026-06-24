use Time, Random;
config const problemSize: int = 1 << 9;
const NITER = 5;

record COOElement { var row: int; var col: int; var value: real; }

proc correctLuFactorize(A: [] COOElement, ref L: [] real, ref U: [] real, N: int) {
  var D: [0..<N*N] real = 0.0;
  for e in A do D[e.row*N+e.col] += e.value;
  L = 0.0; U = 0.0;
  for k in 0..<N {
    for i in k+1..<N { D[i*N+k] /= D[k*N+k]; for j in k+1..<N do D[i*N+j] -= D[i*N+k]*D[k*N+j]; }
  }
  for i in 0..<N do for j in 0..<N {
    if i > j then L[i*N+j] = D[i*N+j];
    else if i == j then { L[i*N+j] = 1.0; U[i*N+j] = D[i*N+j]; }
    else U[i*N+j] = D[i*N+j];
  }
}

proc doValidate(): bool {
  const n = 16;
  for trial in 0..1 {
    var D: [0..<n*n] real; var rs = new randomStream(real, seed=trial+1); rs.fill(D);
    for i in 0..<n do D[i*n+i] += n:real * 5.0;
    var A: [0..<n*n] COOElement;
    for i in 0..<n do for j in 0..<n do A[i*n+j] = new COOElement(i, j, D[i*n+j]);
    var Lc, Uc, Lt, Ut: [0..<n*n] real;
    correctLuFactorize(A, Lc, Uc, n);
    luFactorize(A, Lt, Ut, n);
    for i in Lc.domain do if abs(Lc[i]-Lt[i]) > 1e-6 || abs(Uc[i]-Ut[i]) > 1e-6 then return false;
  }
  return true;
}

proc main() {
  const N = problemSize;
  var D: [0..<N*N] real; var rs = new randomStream(real, seed=42); rs.fill(D);
  for i in 0..<N do D[i*N+i] += N:real * 5.0;
  var A: [0..<N*N] COOElement;
  for i in 0..<N do for j in 0..<N do A[i*N+j] = new COOElement(i, j, D[i*N+j]);
  var L, U: [0..<N*N] real;

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for i in 0..<NITER { sw.restart(); luFactorize(A, L, U, N); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for i in 0..<NITER { sw.restart(); correctLuFactorize(A, L, U, N); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}
