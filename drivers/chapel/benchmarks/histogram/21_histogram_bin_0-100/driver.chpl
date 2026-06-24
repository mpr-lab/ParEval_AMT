use Time, Random;
config const problemSize: int = 1 << 24;
const NITER = 5;

proc correctBinsBy10Count(x: [] real, ref bins: [] int) {
  for v in x {
    var b = (v / 10.0):int;
    if b < 0 then b = 0; if b >= 10 then b = 9;
    bins[b] += 1;
  }
}

proc doValidate(): bool {
  const n = 1024;
  for trial in 0..1 {
    var x: [0..<n] real;
    var rs = new randomStream(real, seed=trial+1);
    rs.fill(x);
    for i in x.domain { x[i] *= 100.0; }
    var bref: [0..<10] int = 0; var bgen: [0..<10] int = 0;
    correctBinsBy10Count(x, bref); binsBy10Count(x, bgen);
    for i in 0..<10 { if bref[i] != bgen[i] then return false; }
  }
  return true;
}

proc main() {
  const n = problemSize;
  var x: [0..<n] real; var bins: [0..<10] int = 0;
  var rs = new randomStream(real, seed=42);
  rs.fill(x);
  for i in x.domain { x[i] *= 100.0; }

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for it in 0..<NITER { bins = 0; sw.restart(); binsBy10Count(x, bins); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for it in 0..<NITER { bins = 0; sw.restart(); correctBinsBy10Count(x, bins); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}
