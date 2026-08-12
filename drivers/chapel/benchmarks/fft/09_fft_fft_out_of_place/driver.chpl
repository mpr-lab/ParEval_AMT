use Time, Random, Math;
config const problemSize: int = 1 << 14;
const NITER = 5;

proc correctFft(x: [] complex(128), ref output: [] complex(128)) {
  const n = x.size;
  for k in 0..<n {
    var re_s = 0.0; var im_s = 0.0;
    for j in 0..<n {
      var angle = -2.0 * Math.PI * k * j / n:real;
      re_s += x[j].re * cos(angle) - x[j].im * sin(angle);
      im_s += x[j].re * sin(angle) + x[j].im * cos(angle);
    }
    output[k].re = re_s; output[k].im = im_s;
  }
}

proc doValidate(): bool {
  const testN = 64;
  for trial in 0..1 {
    var x: [0..<testN] complex(128);
    var rs = new randomStream(real, seed=trial+1);
    for idx in 0..<testN { x[idx].re = rs.next(); x[idx].im = rs.next(); }
    var oref: [0..<testN] complex(128);
    var ogen: [0..<testN] complex(128);
    correctFft(x, oref); fft(x, ogen);
    for idx in 0..<testN {
      if abs(oref[idx].re - ogen[idx].re) > 1e-9 then return false;
      if abs(oref[idx].im - ogen[idx].im) > 1e-9 then return false;
    }
  }
  return true;
}

proc main() {
  const n = problemSize;
  var x: [0..<n] complex(128);
  var output: [0..<n] complex(128);
  var rs = new randomStream(real, seed=42);
  for idx in 0..<n { x[idx].re = rs.next(); x[idx].im = rs.next(); }

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for it in 0..<NITER { sw.restart(); fft(x, output); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for it in 0..<NITER { sw.restart(); correctFft(x, output); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}
