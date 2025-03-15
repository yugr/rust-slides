All info about problems with indexing checks at runtime.

matklad [claims](https://github.com/matklad/bounds-check-cost) that main problem with index checks
is blockage of autovec (and maybe other optimizations) and check themselves are cheap.

# TODO

- Disable index checks in compiler and compare perf of large and/or performance sensitive projects

# Combining multiple checks not optimized

Compiler does not combine multiple related index checks to same slice within same scope into one.
See [upstream #50759](https://github.com/rust-lang/rust/issues/50759) for good example of this.

Basically when accessing `h[0]` and then `h[1]` it has to first check `0` and then `1`
because it tries to report exact error location.

Programmers can use explicit `assert!` macro to allow compiler to optimize checks.
