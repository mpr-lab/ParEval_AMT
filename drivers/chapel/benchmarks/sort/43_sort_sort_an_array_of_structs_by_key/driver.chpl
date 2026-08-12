use Time, Random, Sort;
config const problemSize: int = 1 << 22;
const NITER = 5;

record Result { var startTime, duration: int; var value: real; }

record ResultComparator {
  proc compare(a, b: Result): int {
    if a.startTime < b.startTime then return -1;
    if a.startTime > b.startTime then return 1;
    return 0;
  }
}

proc correctSortByStartTime(ref results: [] Result) {
  var cmp: ResultComparator;
  sort(results, comparator=cmp);
}

proc doValidate(): bool {
  const n = 1024;
  for trial in 0..1 {
    var res: [0..<n] Result;
    var rs = new randomStream(int, seed=trial+1);
    for i in 0..<n { res[i].startTime = rs.next() % 10000; res[i].duration = rs.next() % 100; res[i].value = 1.0; }
    var rref = res; var rgen = res;
    correctSortByStartTime(rref); sortByStartTime(rgen);
    for i in 0..<n { if rref[i].startTime != rgen[i].startTime then return false; }
  }
  return true;
}

proc main() {
  const n = problemSize;
  var results: [0..<n] Result;
  var rs = new randomStream(int, seed=42);
  for i in 0..<n { results[i].startTime = rs.next() % 1000000; results[i].duration = rs.next() % 1000; results[i].value = 1.0; }
  const orig = results;

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for it in 0..<NITER { results = orig; sw.restart(); sortByStartTime(results); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for it in 0..<NITER { results = orig; sw.restart(); correctSortByStartTime(results); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}
