use Time, Random;
config const problemSize: int = 1 << 21;
const NITER = 5;

proc correctMapPowersOfTwo(x: [] int, ref mask: [] bool) {
  for i in x.domain do mask[i] = x[i] > 0 && (x[i] & (x[i] - 1)) == 0;
}

proc doValidate(): bool {
  const n = 1024;
  for trial in 0..1 {
    var a: [0..<n] int;
    var rs = new randomStream(int, seed=trial+1);
    rs.fill(a);
    for i in a.domain do a[i] = (a[i] % 64) + 1;
    var mb, mt: [0..<n] bool;
    correctMapPowersOfTwo(a, mb);
    mapPowersOfTwo(a, mt);
    for i in a.domain do if mb[i] != mt[i] then return false;
  }
  return true;
}

proc main() {
  var x: [0..<problemSize] int;
  var rs = new randomStream(int, seed=42);
  rs.fill(x);
  for i in x.domain do x[i] = (x[i] % 64) + 1;
  var mask: [0..<problemSize] bool;

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for i in 0..<NITER { sw.restart(); mapPowersOfTwo(x, mask); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for i in 0..<NITER { sw.restart(); correctMapPowersOfTwo(x, mask); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}
