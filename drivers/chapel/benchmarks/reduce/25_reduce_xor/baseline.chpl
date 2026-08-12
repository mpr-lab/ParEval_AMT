// Baseline implementation for 25_reduce_xor
// Return the logical XOR reduction of the vector of bools x.
// Example:
//   input: [false, false, false, true]
//   output: true

proc correctReduceLogicalXOR(const x: [] bool): bool {
    var result: bool = false;
    for val in x {
        result = result != val;
    }
    return result;
}
