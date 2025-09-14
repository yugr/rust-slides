This is about various problems with autovec in Rust.

Autovec is a complex feature which is negatively affected by
  - [bounds checking](../bounds-checks/README.md)
  - [lack of fast math](../fastmath/README.md)
On the other hand it's positively affected by
  - [noalias](../../pros/alias/README.md)
  - [chained iterators](../iterators/README.md)

To facilitate vectorization [use](https://www.reddit.com/r/rust/comments/1hk0bry/comment/m3b76gn/)
  - `chunks_exact` iterator (even if length is not divisable, see [this](https://github.com/nnethercote/perf-book/issues/52))
    * TODO: does this facilitate SLP or Loop vectorizer ?

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

# Remarks

Optimization remarks can be used to diagnose reasons for missing autovec:
  - Use [cargo remark](https://kobzol.github.io/rust/cargo/2023/08/12/rust-llvm-optimization-remarks.html) tool
  - Or `RUSTFLAGS="-Cdebuginfo=1 -Cremark=all -Zremark-dir=/tmp/remarks" cargo build --release`
  - Or Specifically for autovec: `-g -O -C llvm-args='--pass-remarks-missed=loop-vectorize --pass-remarks-analysis=loop-vectorize'`
Results can be viewed with optview2 tool.

# TODO

- For all problematic features (e.g. bounds checks) collect how they influence autovec (via LLVM debug)
  * Done in [bounds checks analysis](../bounds/analysis.md)
- Check SLP vs loop autovec stats
  * Low prio
- Try autovec for simple ubenchmarks (DOALL, reduction, strlen)
  * DOALL and reductions vectorize fine, strlen-like loops are not vectorized neither in Rust, nor C
