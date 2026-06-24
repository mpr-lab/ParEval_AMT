use Time, Random;
config const problemSize: int = 1 << 12;
const NITER = 5;

proc correctJacobi2D(input: [] real, ref output: [] real, N: int) {
  for i in 1..<N-1 do for j in 1..<N-1 do
    output[i*N+j] = (input[(i-1)*N+j] + input[(i+1)*N+j] +
                     input[i*N+(j-1)] + input[i*N+(j+1)] + input[i*N+j]) / 5.0;
}

proc doValidate(): bool {
  const n = 64;
  for trial in 0..1 {
    var a: [0..<n*n] real;
    var rs = new randomStream(real, seed=trial+1);
    rs.fill(a);
    var bc, bt: [0..<n*n] real;
    correctJacobi2D(a, bc, n);
    jacobi2D(a, bt, n);
    for i in 1..<n-1 do for j in 1..<n-1 do
      if abs(bc[i*n+j]-bt[i*n+j]) > 1e-10 then return false;
  }
  return true;
}

proc main() {
  const N = problemSize;
  var input: [0..<N*N] real;
  var rs = new randomStream(real, seed=42);
  rs.fill(input);
  var output: [0..<N*N] real;

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for i in 0..<NITER { sw.restart(); jacobi2D(input, output, N); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for i in 0..<NITER { sw.restart(); correctJacobi2D(input, output, N); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}
