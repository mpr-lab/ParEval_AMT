use Time, Random;
config const problemSize: int = 1 << 12;
const NITER = 5;

proc correctCellsXOR(input: [] int, ref output: [] int, N: int) {
  for i in 0..<N do for j in 0..<N {
    var nbrs = 0;
    if i > 0   then nbrs += input[(i-1)*N+j];
    if i < N-1 then nbrs += input[(i+1)*N+j];
    if j > 0   then nbrs += input[i*N+(j-1)];
    if j < N-1 then nbrs += input[i*N+(j+1)];
    output[i*N+j] = if nbrs == 1 then 1 else 0;
  }
}

proc doValidate(): bool {
  const n = 64;
  for trial in 0..1 {
    var a: [0..<n*n] int;
    var rs = new randomStream(int, seed=trial+1);
    rs.fill(a);
    for i in a.domain do a[i] = abs(a[i]) % 2;
    var bc, bt: [0..<n*n] int;
    correctCellsXOR(a, bc, n);
    cellsXOR(a, bt, n);
    for i in a.domain do if bc[i] != bt[i] then return false;
  }
  return true;
}

proc main() {
  const N = problemSize;
  var input: [0..<N*N] int;
  var rs = new randomStream(int, seed=42);
  rs.fill(input);
  for i in input.domain do input[i] = abs(input[i]) % 2;
  var output: [0..<N*N] int;

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for i in 0..<NITER { sw.restart(); cellsXOR(input, output, N); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for i in 0..<NITER { sw.restart(); correctCellsXOR(input, output, N); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}
