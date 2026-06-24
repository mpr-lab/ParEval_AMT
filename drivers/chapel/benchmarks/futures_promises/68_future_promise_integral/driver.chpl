use Time, Math;
config const problemSize: int = 1 << 20;
const NITER = 5;

proc correctIntegrateFunction(a: real, b: real, n: int): real {
  const h = (b - a) / n;
  var s = 0.0;
  for i in 0..<n { const x = a + (i:real + 0.5) * h; s += sin(x) * h; }
  return s;
}

proc doValidate(): bool {
  const n = 10000;
  const correct = correctIntegrateFunction(0.0, Math.pi, n);
  const test    = integrateFunction(0.0, Math.pi, n);
  return abs(correct - test) < 1e-4;
}

proc main() {
  const n = problemSize;

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch; var computeTotal = 0.0;
  for i in 0..<NITER { sw.restart(); var r = integrateFunction(0.0, Math.pi, n); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);
  var bestTotal = 0.0;
  for i in 0..<NITER { sw.restart(); var r = correctIntegrateFunction(0.0, Math.pi, n); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}
