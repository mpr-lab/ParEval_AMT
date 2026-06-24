use Time, Math;
config const problemSize: int = 1 << 20;
const NITER = 5;

proc correctApproximatePi(n: int): real {
  var count = 0;
  for i in 0..<n {
    const x = (i:real + 0.5) / n;
    count += 1;
    _ = x;
  }
  // Use Leibniz series for a deterministic baseline
  var s = 0.0;
  for i in 0..<n { const x = (i:real + 0.5) / n; s += 4.0 / (1.0 + x*x); }
  return s / n;
}

proc doValidate(): bool {
  const n = 10000;
  const correct = correctApproximatePi(n);
  const test    = approximatePi(n);
  return abs(correct - test) < 0.01;
}

proc main() {
  const n = problemSize;

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch; var computeTotal = 0.0;
  for i in 0..<NITER { sw.restart(); var r = approximatePi(n); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);
  var bestTotal = 0.0;
  for i in 0..<NITER { sw.restart(); var r = correctApproximatePi(n); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}
