use Time, Random, Math;
config const problemSize: int = 1 << 24;
const NITER = 5;

proc correctFftConjugate(ref x: [] complex(128)) {
  const n = x.size;
  for i in x.domain { x[i].im = -x[i].im; x[i].re /= n:real; x[i].im /= n:real; }
}

proc doValidate(): bool {
  const testN = 1024;
  for trial in 0..1 {
    var x: [0..<testN] complex(128);
    var rs = new randomStream(real, seed=trial+1);
    for i in 0..<testN { x[i].re = rs.rand(); x[i].im = rs.rand(); }
    var xref = x; var xgen = x;
    correctFftConjugate(xref); fftConjugate(xgen);
    for i in 0..<testN {
      if abs(xref[i].re - xgen[i].re) > 1e-12 then return false;
      if abs(xref[i].im - xgen[i].im) > 1e-12 then return false;
    }
  }
  return true;
}

proc main() {
  const n = problemSize;
  var x: [0..<n] complex(128);
  var rs = new randomStream(real, seed=42);
  for i in 0..<n { x[i].re = rs.rand(); x[i].im = rs.rand(); }
  const xorig = x;

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for it in 0..<NITER { x = xorig; sw.restart(); fftConjugate(x); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for it in 0..<NITER { x = xorig; sw.restart(); correctFftConjugate(x); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}
