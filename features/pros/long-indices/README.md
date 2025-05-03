This describes benefits from forced `size_t` indexes in Rust.

Rust forces programmer to use 64-bit indexes.
They do not need to be zero-extended so converting `a[i]`'s
to induction variables becomes trivial.
See [Overflow UB in C++](../../cons/arithmetic-checks/overflow-checks/README.md)
for problems caused by small indexes in C++.
