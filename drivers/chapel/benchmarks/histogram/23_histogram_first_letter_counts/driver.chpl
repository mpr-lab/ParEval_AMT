use Time, Random;
config const problemSize: int = 1 << 22;
const NITER = 5;

const ALPHA: [0..<26] string = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"];

proc correctFirstLetterCounts(s: [] string, ref bins: [] int) {
  for str in s {
    for b in 0..<26 { if str.startsWith(ALPHA[b]) { bins[b] += 1; break; } }
  }
}

proc makeStrings(ref s: [] string, rs: randomStream(int)) {
  for i in s.domain {
    var idx = ((rs.next() % 26) + 26) % 26;
    s[i] = ALPHA[idx];
  }
}

proc doValidate(): bool {
  const n = 1024;
  for trial in 0..1 {
    var s: [0..<n] string;
    var rs = new randomStream(int, seed=trial+1);
    makeStrings(s, rs);
    var bref: [0..<26] int = 0; var bgen: [0..<26] int = 0;
    correctFirstLetterCounts(s, bref); firstLetterCounts(s, bgen);
    for i in 0..<26 { if bref[i] != bgen[i] then return false; }
  }
  return true;
}

proc main() {
  const n = problemSize;
  var s: [0..<n] string; var bins: [0..<26] int = 0;
  var rs = new randomStream(int, seed=42);
  makeStrings(s, rs);

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for it in 0..<NITER { bins = 0; sw.restart(); firstLetterCounts(s, bins); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for it in 0..<NITER { bins = 0; sw.restart(); correctFirstLetterCounts(s, bins); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}
