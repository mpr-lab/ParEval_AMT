use Time, Random, Math;
config const problemSize: int = 1 << 24;
const NITER = 5;

proc correctFindClosestToPi(x: [] real): int {
  var minD = abs(x[0] - Math.PI); var minIdx = 0;
  for i in 1..<x.size {
    var d = abs(x[i] - Math.PI);
    if d < minD { minD = d; minIdx = i; }
  }
  return minIdx;
}

proc doValidate(): bool {
  const n = 1024;
  for trial in 0..1 {
    var x: [0..<n] real;
    var rs = new randomStream(real, seed=trial+1);
    rs.fill(x);
    for i in x.domain { x[i] = x[i] * 6.0 + 0.14; }
    if correctFindClosestToPi(x) != findClosestToPi(x) then return false;
  }
  return true;
}

proc main() {
  const n = problemSize;
  var x: [0..<n] real;
  var rs = new randomStream(real, seed=42);
  rs.fill(x);
  for i in x.domain { x[i] = x[i] * 6.0 + 0.14; }

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for it in 0..<NITER { sw.restart(); var r = findClosestToPi(x); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for it in 0..<NITER { sw.restart(); var r = correctFindClosestToPi(x); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}
