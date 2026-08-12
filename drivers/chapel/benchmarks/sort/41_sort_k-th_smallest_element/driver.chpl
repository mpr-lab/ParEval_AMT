use Time, Random, Sort;
config const problemSize: int = 1 << 22;
const NITER = 5;

proc correctFindKthSmallest(x: [] int, k: int): int {
  var sorted = x; sort(sorted); return sorted[k-1];
}

proc doValidate(): bool {
  const n = 1024;
  for trial in 0..1 {
    var x: [0..<n] int;
    var rs = new randomStream(int, seed=trial+1);
    for i in x.domain { x[i] = rs.rand() % 10000; }
    const k = n/2;
    if correctFindKthSmallest(x, k) != findKthSmallest(x, k) then return false;
  }
  return true;
}

proc main() {
  const n = problemSize;
  var x: [0..<n] int;
  var rs = new randomStream(int, seed=42);
  for i in x.domain { x[i] = rs.rand() % 1000000; }
  const k = n/2;

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for it in 0..<NITER { sw.restart(); var r = findKthSmallest(x, k); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for it in 0..<NITER { sw.restart(); var r = correctFindKthSmallest(x, k); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}
