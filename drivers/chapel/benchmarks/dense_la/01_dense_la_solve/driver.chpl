use Time, Random, Math;
config const problemSize: int = 1 << 18;
const NITER = 5;

proc correctSolveLinearSystem(A: [] real, b: [] real, ref x: [] real, N: int) {
  var Ac: [0..<N*N] real = A;
  var bc: [0..<N] real = b;
  for k in 0..<N {
    var maxVal = abs(Ac[k*N+k]); var maxRow = k;
    for i in k+1..<N { if abs(Ac[i*N+k]) > maxVal { maxVal = abs(Ac[i*N+k]); maxRow = i; } }
    if maxRow != k {
      for j in 0..<N { var tmp = Ac[k*N+j]; Ac[k*N+j] = Ac[maxRow*N+j]; Ac[maxRow*N+j] = tmp; }
      var tmp = bc[k]; bc[k] = bc[maxRow]; bc[maxRow] = tmp;
    }
    for i in k+1..<N {
      var f = Ac[i*N+k] / Ac[k*N+k];
      for j in k..<N { Ac[i*N+j] -= f * Ac[k*N+j]; }
      bc[i] -= f * bc[k];
    }
  }
  for ik in 0..<N {
    var i = N-1-ik;
    x[i] = bc[i];
    for j in i+1..<N { x[i] -= Ac[i*N+j] * x[j]; }
    x[i] /= Ac[i*N+i];
  }
}

proc doValidate(): bool {
  const testN = 32;
  for trial in 0..1 {
    var A: [0..<testN*testN] real;
    var b: [0..<testN] real;
    var rs = new randomStream(real, seed=trial+1);
    rs.fill(A); rs.fill(b);
    for i in 0..<testN { A[i*testN+i] += testN:real; }
    var xref: [0..<testN] real = 0.0;
    var xgen: [0..<testN] real = 0.0;
    correctSolveLinearSystem(A, b, xref, testN);
    solveLinearSystem(A, b, xgen, testN);
    for i in 0..<testN { if abs(xref[i] - xgen[i]) > 1e-6 then return false; }
  }
  return true;
}

proc main() {
  const N = (sqrt(problemSize:real)):int;
  var A: [0..<N*N] real;
  var b: [0..<N] real;
  var x: [0..<N] real;
  var rs = new randomStream(real, seed=42);
  rs.fill(A); rs.fill(b);
  for i in 0..<N { A[i*N+i] += N:real; }

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for it in 0..<NITER { x = 0.0; sw.restart(); solveLinearSystem(A, b, x, N); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for it in 0..<NITER { x = 0.0; sw.restart(); correctSolveLinearSystem(A, b, x, N); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}
