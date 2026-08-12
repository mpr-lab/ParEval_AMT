use Time, Random;
config const problemSize: int = 1 << 21;
const NITER = 5;

record Element { var index: int; var value: real; }

proc correctSparseAxpy(alpha: real, x: [] Element, y: [] Element, ref z: [] real) {
  z = 0.0;
  for e in x do z[e.index] += alpha * e.value;
  for e in y do z[e.index] += e.value;
}

proc doValidate(): bool {
  const n = 1024; const nnz = 128;
  for trial in 0..1 {
    var x: [0..<nnz] Element; var y: [0..<nnz] Element;
    var rs = new randomStream(real, seed=trial+1);
    for i in x.domain { x[i].index = (rs.rand()*n):int % n; x[i].value = rs.rand()*2-1; }
    for i in y.domain { y[i].index = (rs.rand()*n):int % n; y[i].value = rs.rand()*2-1; }
    var zc, zt: [0..<n] real;
    correctSparseAxpy(2.0, x, y, zc);
    sparseAxpy(2.0, x, y, zt);
    for i in zc.domain do if abs(zc[i]-zt[i]) > 1e-10 then return false;
  }
  return true;
}

proc main() {
  const n = problemSize; const nnz = problemSize / 10;
  var x: [0..<nnz] Element; var y: [0..<nnz] Element; var z: [0..<n] real;
  var rs = new randomStream(real, seed=42);
  for i in x.domain { x[i].index = (rs.rand()*n):int % n; x[i].value = rs.rand()*2-1; }
  for i in y.domain { y[i].index = (rs.rand()*n):int % n; y[i].value = rs.rand()*2-1; }
  const alpha = 2.0;

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for i in 0..<NITER { sw.restart(); sparseAxpy(alpha, x, y, z); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for i in 0..<NITER { sw.restart(); correctSparseAxpy(alpha, x, y, z); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}
