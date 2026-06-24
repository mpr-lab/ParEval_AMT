use Time, Random;
config const problemSize: int = 1 << 10;
const NITER = 5;

record COOElement { var row: int; var col: int; var value: real; }

proc correctSolveLinearSystem(A: [] COOElement, b: [] real, ref x: [] real, N: int) {
  // Dense reconstruction + Gaussian elimination
  var D: [0..<N*N] real = 0.0;
  for e in A do D[e.row*N+e.col] += e.value;
  var bc = b;
  for k in 0..<N {
    for i in k+1..<N {
      const f = D[i*N+k] / D[k*N+k];
      for j in k..<N do D[i*N+j] -= f * D[k*N+j];
      bc[i] -= f * bc[k];
    }
  }
  for i in 0..<N by -1 { x[i] = bc[i]; for j in i+1..<N do x[i] -= D[i*N+j]*x[j]; x[i] /= D[i*N+i]; }
}

proc doValidate(): bool {
  const n = 32;
  for trial in 0..1 {
    var D: [0..<n*n] real; var b: [0..<n] real;
    var rs = new randomStream(real, seed=trial+1);
    rs.fill(D); rs.fill(b);
    for i in 0..<n do D[i*n+i] += n:real * 5.0;
    var A: [0..<n*n] COOElement;
    for i in 0..<n do for j in 0..<n do A[i*n+j] = new COOElement(i, j, D[i*n+j]);
    var xc, xt: [0..<n] real;
    correctSolveLinearSystem(A, b, xc, n);
    solveLinearSystem(A, b, xt, n);
    for i in xc.domain do if abs(xc[i]-xt[i]) > 1e-4 then return false;
  }
  return true;
}

proc main() {
  const N = problemSize;
  var D: [0..<N*N] real; var b: [0..<N] real;
  var rs = new randomStream(real, seed=42);
  rs.fill(D); rs.fill(b);
  for i in 0..<N do D[i*N+i] += N:real * 5.0;
  var A: [0..<N*N] COOElement;
  for i in 0..<N do for j in 0..<N do A[i*N+j] = new COOElement(i, j, D[i*N+j]);
  var x: [0..<N] real;

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for i in 0..<NITER { sw.restart(); solveLinearSystem(A, b, x, N); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for i in 0..<NITER { sw.restart(); correctSolveLinearSystem(A, b, x, N); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}
