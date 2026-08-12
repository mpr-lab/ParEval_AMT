use Time, Random, Math;
config const problemSize: int = 1 << 14;
const NITER = 5;

proc correctFftSplit(x: [] complex(128), ref rOut: [] real, ref iOut: [] real) {
  const n = x.size;
  for k in 0..<n {
    var re_s = 0.0; var im_s = 0.0;
    for j in 0..<n {
      var angle = -2.0 * Math.PI * k * j / n:real;
      re_s += x[j].re * cos(angle) - x[j].im * sin(angle);
      im_s += x[j].re * sin(angle) + x[j].im * cos(angle);
    }
    rOut[k] = re_s; iOut[k] = im_s;
  }
}

proc doValidate(): bool {
  const testN = 64;
  for trial in 0..1 {
    var x: [0..<testN] complex(128);
    var rs = new randomStream(real, seed=trial+1);
    for idx in 0..<testN { x[idx].re = rs.rand(); x[idx].im = rs.rand(); }
    var rref: [0..<testN] real; var iref: [0..<testN] real;
    var rgen: [0..<testN] real; var igen: [0..<testN] real;
    correctFftSplit(x, rref, iref);
    fft(x, rgen, igen);
    for idx in 0..<testN {
      if abs(rref[idx] - rgen[idx]) > 1e-9 then return false;
      if abs(iref[idx] - igen[idx]) > 1e-9 then return false;
    }
  }
  return true;
}

proc main() {
  const n = problemSize;
  var x: [0..<n] complex(128);
  var r: [0..<n] real; var im: [0..<n] real;
  var rs = new randomStream(real, seed=42);
  for idx in 0..<n { x[idx].re = rs.rand(); x[idx].im = rs.rand(); }

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for it in 0..<NITER { sw.restart(); fft(x, r, im); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for it in 0..<NITER { sw.restart(); correctFftSplit(x, r, im); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}
