use Time, Random, Math, Sort;
config const problemSize: int = 1 << 24;
const NITER = 5;

proc correctClosestPair(x: [] real): real {
  var sorted = x;
  sort(sorted);
  var minD = max(real);
  for i in 1..<x.size {
    var d = abs(sorted[i] - sorted[i-1]);
    if d < minD then minD = d;
  }
  return minD;
}

proc doValidate(): bool {
  const testN = 1024;
  for trial in 0..1 {
    var x: [0..<testN] real;
    var rs = new randomStream(real, seed=trial+1);
    rs.fill(x);
    if abs(correctClosestPair(x) - closestPair(x)) > 1e-12 then return false;
  }
  return true;
}

proc main() {
  const n = problemSize;
  var x: [0..<n] real;
  var rs = new randomStream(real, seed=42);
  rs.fill(x);

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for it in 0..<NITER { sw.restart(); var r = closestPair(x); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for it in 0..<NITER { sw.restart(); var r = correctClosestPair(x); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}
