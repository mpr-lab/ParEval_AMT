use Time, Random;
config const problemSize: int = 1 << 24;
const NITER = 5;

proc correctPartialMinimums(ref x: [] real) {
  for i in 1..<x.size { if x[i] > x[i-1] then x[i] = x[i-1]; }
}

proc doValidate(): bool {
  const n = 1024;
  for trial in 0..1 {
    var x: [0..<n] real;
    var rs = new randomStream(real, seed=trial+1); rs.fill(x);
    var xref = x; var xgen = x;
    correctPartialMinimums(xref); partialMinimums(xgen);
    for i in 0..<n { if abs(xref[i] - xgen[i]) > 1e-12 then return false; }
  }
  return true;
}

proc main() {
  const n = problemSize;
  var x: [0..<n] real;
  var rs = new randomStream(real, seed=42); rs.fill(x);
  const orig = x;

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for it in 0..<NITER { x = orig; sw.restart(); partialMinimums(x); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for it in 0..<NITER { x = orig; sw.restart(); correctPartialMinimums(x); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}
