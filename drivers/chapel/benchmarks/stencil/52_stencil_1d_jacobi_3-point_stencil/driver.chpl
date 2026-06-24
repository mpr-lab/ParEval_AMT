use Time, Random;
config const problemSize: int = 1 << 23;
const NITER = 5;

proc correctJacobi1D(input: [] real, ref output: [] real) {
  const n = input.size;
  output[0] = input[0]; output[n-1] = input[n-1];
  for i in 1..<n-1 do output[i] = (input[i-1] + input[i] + input[i+1]) / 3.0;
}

proc doValidate(): bool {
  const n = 1024;
  for trial in 0..1 {
    var a: [0..<n] real;
    var rs = new randomStream(real, seed=trial+1);
    rs.fill(a);
    var bc, bt: [0..<n] real;
    correctJacobi1D(a, bc);
    jacobi1D(a, bt);
    for i in a.domain do if abs(bc[i]-bt[i]) > 1e-10 then return false;
  }
  return true;
}

proc main() {
  var input: [0..<problemSize] real;
  var rs = new randomStream(real, seed=42);
  rs.fill(input);
  var output: [0..<problemSize] real;

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for i in 0..<NITER { sw.restart(); jacobi1D(input, output); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for i in 0..<NITER { sw.restart(); correctJacobi1D(input, output); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}
