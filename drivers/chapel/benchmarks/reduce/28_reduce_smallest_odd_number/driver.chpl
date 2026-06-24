use Time, Random;
config const problemSize: int = 1 << 24;
const NITER = 5;

proc correctSmallestOdd(x: [] int): int {
  var m = max(int);
  for v in x do if v % 2 != 0 && v < m then m = v;
  return m;
}

proc doValidate(): bool {
  const n = 1024;
  for trial in 0..1 {
    var a: [0..<n] int;
    var rs = new randomStream(int, seed=trial+1);
    rs.fill(a);
    for i in a.domain do a[i] = (a[i] % 200) - 100;
    a[0] = 1; // guarantee at least one odd
    if correctSmallestOdd(a) != smallestOdd(a) then return false;
  }
  return true;
}

proc main() {
  var x: [0..<problemSize] int;
  var rs = new randomStream(int, seed=42);
  rs.fill(x);
  for i in x.domain do x[i] = (x[i] % 200) - 100;
  x[0] = 1;

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for i in 0..<NITER { sw.restart(); var r = smallestOdd(x); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for i in 0..<NITER { sw.restart(); var r = correctSmallestOdd(x); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}
