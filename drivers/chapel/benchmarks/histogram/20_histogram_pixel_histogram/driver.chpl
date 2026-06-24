use Time, Random;
config const problemSize: int = 1 << 24;
const NITER = 5;

proc correctPixelCounts(image: [] int, ref bins: [] int) {
  for v in image { bins[v] += 1; }
}

proc doValidate(): bool {
  const n = 1024;
  for trial in 0..1 {
    var image: [0..<n] int;
    var rs = new randomStream(int, seed=trial+1);
    for i in image.domain { image[i] = ((rs.getNext() % 256) + 256) % 256; }
    var bref: [0..<256] int = 0; var bgen: [0..<256] int = 0;
    correctPixelCounts(image, bref); pixelCounts(image, bgen);
    for i in 0..<256 { if bref[i] != bgen[i] then return false; }
  }
  return true;
}

proc main() {
  const n = problemSize;
  var image: [0..<n] int;
  var bins: [0..<256] int = 0;
  var rs = new randomStream(int, seed=42);
  for i in image.domain { image[i] = ((rs.getNext() % 256) + 256) % 256; }

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for it in 0..<NITER { bins = 0; sw.restart(); pixelCounts(image, bins); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for it in 0..<NITER { bins = 0; sw.restart(); correctPixelCounts(image, bins); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}
