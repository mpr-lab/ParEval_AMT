use Time, Random;
config const problemSize: int = 1 << 10;
const NITER = 5;

proc correctJacobi(A: [] real, b: [] real, ref x: [] real, N: int, maxIter: int) {
  var xNew: [0..<N] real;
  for _ in 0..<maxIter {
    for i in 0..<N {
      xNew[i] = b[i];
      for j in 0..<N do if j != i then xNew[i] -= A[i*N+j] * x[j];
      xNew[i] /= A[i*N+i];
    }
    x = xNew;
  }
}

proc doValidate(): bool {
  const n = 32;
  for trial in 0..1 {
    var A: [0..<n*n] real; var b: [0..<n] real; var rs = new randomStream(real, seed=trial+1);
    rs.fill(A); rs.fill(b);
    for i in 0..<n do A[i*n+i] += n:real * 10.0;
    var xc, xt: [0..<n] real;
    correctJacobi(A, b, xc, n, 50); jacobi(A, b, xt, n, 50);
    for i in xc.domain do if abs(xc[i]-xt[i]) > 1e-6 then return false;
  }
  return true;
}

proc main() {
  const N = problemSize; var A: [0..<N*N] real; var b: [0..<N] real; var x: [0..<N] real;
  var rs = new randomStream(real, seed=42); rs.fill(A); rs.fill(b);
  for i in 0..<N do A[i*N+i] += N:real * 10.0;

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch; var computeTotal = 0.0;
  for i in 0..<NITER { x = 0.0; sw.restart(); jacobi(A, b, x, N, 50); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);
  var bestTotal = 0.0;
  for i in 0..<NITER { x = 0.0; sw.restart(); correctJacobi(A, b, x, N, 50); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}
