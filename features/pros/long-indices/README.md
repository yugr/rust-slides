This describes benefits from forced `size_t` indexes in Rust.

64-bit indexes do not need to be zero-extended and so making addresses
to induction variables becomes trivial.
See [Overflow UB in C++](../../cons/arithmetic-checks/overflow-checks/README.md)
for problems caused by small indexes in C++.
