use Time, Random;
config const problemSize: int = 1 << 12;
const NITER = 5;

proc correctConvolveKernel(imageIn: [] int, ref imageOut: [] int, N: int) {
  for i in 1..<N-1 do for j in 1..<N-1 {
    imageOut[i*N+j] =
      -imageIn[(i-1)*N+(j-1)] - imageIn[(i-1)*N+j] - imageIn[(i-1)*N+(j+1)]
      -imageIn[i*N+(j-1)]     + 8*imageIn[i*N+j]   - imageIn[i*N+(j+1)]
      -imageIn[(i+1)*N+(j-1)] - imageIn[(i+1)*N+j] - imageIn[(i+1)*N+(j+1)];
  }
}

proc doValidate(): bool {
  const n = 64;
  for trial in 0..1 {
    var a: [0..<n*n] int;
    var rs = new randomStream(int, seed=trial+1);
    rs.fill(a);
    for i in a.domain do a[i] = abs(a[i]) % 256;
    var bc, bt: [0..<n*n] int;
    correctConvolveKernel(a, bc, n);
    convolveKernel(a, bt, n);
    for i in 1..<n-1 do for j in 1..<n-1 do if bc[i*n+j] != bt[i*n+j] then return false;
  }
  return true;
}

proc main() {
  const N = problemSize;
  var imageIn: [0..<N*N] int;
  var rs = new randomStream(int, seed=42);
  rs.fill(imageIn);
  for i in imageIn.domain do imageIn[i] = abs(imageIn[i]) % 256;
  var imageOut: [0..<N*N] int;

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for i in 0..<NITER { sw.restart(); convolveKernel(imageIn, imageOut, N); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for i in 0..<NITER { sw.restart(); correctConvolveKernel(imageIn, imageOut, N); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}
