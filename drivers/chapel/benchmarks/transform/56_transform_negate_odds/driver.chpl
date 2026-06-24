use Time, Random;
config const problemSize: int = 1 << 21;
const NITER = 5;

proc correctNegateOddsAndHalveEvens(ref x: [] int) {
  for i in x.domain {
    if x[i] % 2 != 0 then x[i] = -x[i];
    else x[i] /= 2;
  }
}

proc doValidate(): bool {
  const n = 1024;
  for trial in 0..1 {
    var a: [0..<n] int;
    var rs = new randomStream(int, seed=trial+1);
    rs.fill(a);
    for i in a.domain do a[i] = (a[i] % 200) - 100;
    var b = a;
    correctNegateOddsAndHalveEvens(b);
    negateOddsAndHalveEvens(a);
    for i in a.domain do if a[i] != b[i] then return false;
  }
  return true;
}

proc main() {
  var x: [0..<problemSize] int;
  var rs = new randomStream(int, seed=42);
  rs.fill(x);
  for i in x.domain do x[i] = (x[i] % 200) - 100;
  const orig = x;

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for i in 0..<NITER { x = orig; sw.restart(); negateOddsAndHalveEvens(x); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for i in 0..<NITER { x = orig; sw.restart(); correctNegateOddsAndHalveEvens(x); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}
