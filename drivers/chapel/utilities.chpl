// Chapel utilities module
// This module provides common utilities for Chapel benchmarks

module Utilities {
    use IO;
    use Random;
    use Time;
    use Comm;

    // Define problem size - will be set during compilation
    const DRIVER_PROBLEM_SIZE: int = 1<<20;
    const MAX_VALIDATION_ATTEMPTS: int = 2;

    // Check if we are the root process (for MPI)
    proc isRoot(): bool {
        return myRank() == 0;
    }

    // Get current rank
    proc myRank(): int {
        return if Comm.numLocales() > 0 then Comm.myLocale().id else 0;
    }

    // Synchronize all processes
    proc sync() {
        if Comm.numLocales() > 0 {
            Comm.broadcast();
        }
    }

    // Broadcast a boolean value
    proc broadcastBool(ref x: bool) {
        var tmp = [x];
        if Comm.numLocales() > 0 {
            Comm.broadcast(tmp, 0);
        }
        x = tmp[0];
    }

    // Broadcast a vector of booleans
    proc broadcastBools(ref x: []) {
        if Comm.numLocales() > 0 {
            Comm.broadcast(x, 0);
        }
    }

    // Fill a vector with random boolean values
    proc fillRand(ref x: [] bool, min: bool = false, max: bool = true) {
        var rng = new Random();
        for i in 0..<x.size {
            x[i] = rng.genBool();
        }
    }

    // Fill a vector with random values of any type
    proc fillRand(ref x: []) {
        var rng = new Random();
        for i in 0..<x.size {
            if x.eltType == int {
                x[i] = rng.genInt();
            } else if x.eltType == real {
                x[i] = rng.genReal();
            } else if x.eltType == bool {
                x[i] = rng.genBool();
            }
        }
    }

    // Compare two vectors for equality (with tolerance for floating point)
    proc fequal(const a: [], const b: [], epsilon: real = 1e-6): bool {
        if a.size != b.size {
            return false;
        }
        
        for i in 0..<a.size {
            if a.eltType == real {
                if |a[i] - b[i]| > epsilon {
                    return false;
                }
            } else if a[i] != b[i] {
                return false;
            }
        }
        return true;
    }
}
