This is about various problems with autovec in Rust.

Autovec is a complex feature which is negatively affected by
  - [bounds checking](../bounds-checks/README.md)
  - [lack of fast math](../fastmath/README.md)
On the other hand it's positively affected by
  - [noalias](../../pros/alias/README.md)
  - [chained iterators](../iterators/README.md)

To facilitate vectorization [use](https://www.reddit.com/r/rust/comments/1hk0bry/comment/m3b76gn/)
  - `chunks_exact` iterator (even if length is not divisable, see [this](https://github.com/nnethercote/perf-book/issues/52))

Autovec is [unreliable](https://www.reddit.com/r/rust/comments/1hk0bry/comment/m3c4s6s/)
> risks bad code-gen depending on surrounding code, architectures, types, compiler versions, etc.
but can be tested at compile-time
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

Rust also does not yet support multiversioning.
There are [proposals](https://rust-lang.github.io/rust-project-goals/2025h1/simd-multiversioning.html)
but currently people have to do it [by hand](https://tweedegolf.nl/en/blog/153/simd-in-zlib-rs-part-1-autovectorization-and-target-features).

# TODO

- For all problematic features (e.g. bounds checks) collect how they influence autovec (via LLVM debug)
- Check SLP vs loop autovec stats
