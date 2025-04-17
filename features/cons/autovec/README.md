This is about various problems with autovec in Rust.

Autovec is a complex feature which is negatively affected by
  - [bounds checking](../bounds-checks/README.md)
  - [lack of fast match](../fastmath/README.md)
On the other hand it's positively affected by
  - [noalias](../../pros/alias/README.md)

Autovec is unreliable but can be tested at compile-time
via `-C remark=loop-vectorize` or `-C llvm-args='--pass-remarks=vectorize'`
(sadly [not showing](https://github.com/rust-lang/rust/issues/54048) good location for iterators,
similar to Clang's `-Rpass=loop-vectorize -Rpass-missed=loop-vectorize`).
On the other hand
> in Rust we've found that once it starts working,
> it tends to keep working across compiler versions with no issues
(from [here](https://www.reddit.com/r/rust/comments/1ha7uyi/comment/m16ke06/)).
On the other hand people also [claim](https://www.reddit.com/r/rust/comments/1ha7uyi/comment/m1978ve/)
it's unstable across releases:
> few changes to improve compilation speed over the past n releases
> have had terrible ramifications for codegen

On a positive side, it's portable (to some extent).
