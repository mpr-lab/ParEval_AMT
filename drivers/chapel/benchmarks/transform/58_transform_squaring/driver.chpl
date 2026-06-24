use Time, Random;
config const problemSize: int = 1 << 22;
const NITER = 5;

proc correctSquareEach(ref x: [] int) {
  for i in x.domain do x[i] *= x[i];
}

proc doValidate(): bool {
  const n = 1024;
  for trial in 0..1 {
    var a: [0..<n] int;
    var rs = new randomStream(int, seed=trial+1);
    rs.fill(a);
    for i in a.domain do a[i] = (a[i] % 100) + 1;
    var b = a;
    correctSquareEach(b);
    squareEach(a);
    for i in a.domain do if a[i] != b[i] then return false;
  }
  return true;
}

proc main() {
  var x: [0..<problemSize] int;
  var rs = new randomStream(int, seed=42);
  rs.fill(x);
  for i in x.domain do x[i] = (x[i] % 100) + 1;
  const orig = x;

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for i in 0..<NITER { x = orig; sw.restart(); squareEach(x); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for i in 0..<NITER { x = orig; sw.restart(); correctSquareEach(x); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}
