use Time, Random, Math;
config const problemSize: int = 1 << 14;
const NITER = 5;

proc correctDft(x: [] real, ref output: [] complex(128)) {
  const n = x.size;
  for k in 0..<n {
    var re_s = 0.0; var im_s = 0.0;
    for j in 0..<n {
      var angle = -2.0 * Math.PI * k * j / n:real;
      re_s += x[j] * cos(angle); im_s += x[j] * sin(angle);
    }
    output[k].re = re_s; output[k].im = im_s;
  }
}

proc doValidate(): bool {
  const testN = 64;
  for trial in 0..1 {
    var x: [0..<testN] real;
    var rs = new randomStream(real, seed=trial+1);
    rs.fill(x);
    var oref: [0..<testN] complex(128);
    var ogen: [0..<testN] complex(128);
    correctDft(x, oref); dft(x, ogen);
    for i in 0..<testN {
      if abs(oref[i].re - ogen[i].re) > 1e-9 then return false;
      if abs(oref[i].im - ogen[i].im) > 1e-9 then return false;
    }
  }
  return true;
}

proc main() {
  const n = problemSize;
  var x: [0..<n] real;
  var output: [0..<n] complex(128);
  var rs = new randomStream(real, seed=42);
  rs.fill(x);

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for it in 0..<NITER {
    for i in 0..<n { output[i].re = 0.0; output[i].im = 0.0; }
    sw.restart(); dft(x, output); sw.stop(); computeTotal += sw.elapsed();
  }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for it in 0..<NITER {
    for i in 0..<n { output[i].re = 0.0; output[i].im = 0.0; }
    sw.restart(); correctDft(x, output); sw.stop(); bestTotal += sw.elapsed();
  }
  writeln("BestSequential: ", bestTotal / NITER);
}
