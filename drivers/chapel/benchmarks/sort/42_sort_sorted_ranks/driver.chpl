use Time, Random, Sort;
config const problemSize: int = 1 << 22;
const NITER = 5;

proc correctRanks(x: [] real, ref r: [] int) {
  const n = x.size;
  var pairs: [0..<n] (real, int);
  for i in 0..<n { pairs[i] = (x[i], i); }
  sort(pairs);
  for rank in 0..<n { r[pairs[rank](1)] = rank + 1; }
}

proc doValidate(): bool {
  const n = 1024;
  for trial in 0..1 {
    var x: [0..<n] real; var rref: [0..<n] int = 0; var rgen: [0..<n] int = 0;
    var rs = new randomStream(real, seed=trial+1); rs.fill(x);
    correctRanks(x, rref); ranks(x, rgen);
    for i in 0..<n { if rref[i] != rgen[i] then return false; }
  }
  return true;
}

proc main() {
  const n = problemSize;
  var x: [0..<n] real; var r: [0..<n] int;
  var rs = new randomStream(real, seed=42); rs.fill(x);

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for it in 0..<NITER { r = 0; sw.restart(); ranks(x, r); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for it in 0..<NITER { r = 0; sw.restart(); correctRanks(x, r); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}
