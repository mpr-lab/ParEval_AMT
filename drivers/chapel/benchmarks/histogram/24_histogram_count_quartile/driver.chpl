use Time, Random, Sort;
config const problemSize: int = 1 << 24;
const NITER = 5;

proc correctCountQuartiles(x: [] real, ref bins: [] int) {
  var sorted = x; sort(sorted);
  const n = x.size;
  const q1 = sorted[n/4]; const q2 = sorted[n/2]; const q3 = sorted[3*n/4];
  for v in x {
    if v < q1 then bins[0] += 1;
    else if v < q2 then bins[1] += 1;
    else if v < q3 then bins[2] += 1;
    else bins[3] += 1;
  }
}

proc doValidate(): bool {
  const n = 1024;
  for trial in 0..1 {
    var x: [0..<n] real;
    var rs = new randomStream(real, seed=trial+1);
    rs.fill(x);
    var bref: [0..<4] int = 0; var bgen: [0..<4] int = 0;
    correctCountQuartiles(x, bref); countQuartiles(x, bgen);
    for i in 0..<4 { if bref[i] != bgen[i] then return false; }
  }
  return true;
}

proc main() {
  const n = problemSize;
  var x: [0..<n] real; var bins: [0..<4] int = 0;
  var rs = new randomStream(real, seed=42);
  rs.fill(x);

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for it in 0..<NITER { bins = 0; sw.restart(); countQuartiles(x, bins); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for it in 0..<NITER { bins = 0; sw.restart(); correctCountQuartiles(x, bins); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}
