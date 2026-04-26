This is about various problems with autovec in Rust.

Autovec is a complex feature which is negatively affected by
  - [bounds checking](../bounds-checks/README.md)
  - [lack of fast math](../fastmath/README.md)
On the other hand it's positively affected by
  - [noalias](../../pros/alias/README.md)
  - [chained iterators](../iterators/README.md)

THIS IS NOT A DEDICATED FEATURE, IT SHOULD BE COVERED IN SEPARATE FEATURES.

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

Per Vognsen [mentions](https://github.com/yugr/rust-slides/issues/59#issue-4290388407)
that explicit chunking is good and reliable way to trigger autovec:
> explicit chunking (vs explicit vectorization) is usually sufficient
> to enable auto-vectorization and has some advantages
> compared to explicit vectorization with something like the (non-stable) std::simd
> but of course also has disadvantages.

Rust stdlib has no stable and portable SIMD intrinsics.
(std::simd portable API is stuck in nightly).
So performance-critical Rust either depends on nightly,
uses third-party crates (packed_simd, wide) or
hand-codes std::arch with extensive #[cfg(target_arch)] scaffolding.

# Remarks

Optimization remarks can be used to diagnose reasons for missing autovec:
  - Use [cargo remark](https://kobzol.github.io/rust/cargo/2023/08/12/rust-llvm-optimization-remarks.html) tool
  - Or `RUSTFLAGS="-Cdebuginfo=1 -Cremark=all -Zremark-dir=/tmp/remarks" cargo build --release`
  - Or Specifically for autovec: `-g -O -C llvm-args='--pass-remarks-missed=loop-vectorize --pass-remarks-analysis=loop-vectorize'`
Results can be viewed with optview2 tool.

# More remarks

Autovec is not really pros or cons, just an optimization which can be negatively
(or positively) affected by other language features
(currently bounds checking, lack of fast math and noalias).
We should study and measure these effects while investigating said features.

The only thing worth discussing here is helping compiler to autovectorize
by structuring the code appropriately.

Many people suggest to use explicit `chunks_exact` to help autovec.
In particular [Rust png library](https://github.com/image-rs/image-png)
uses this approach extensively: the original scalar code
```
    x
        .iter()
        .zip(y.iter())
        .map(|(&x_val, &y_val)| {
            (x_val ^ y_val).count_ones()
        })
        .sum::<u32>();
```
is replaced with explicit chunks:
```
    x
        .chunks_exact(8)
        .zip(y.chunks_exact(8))
        .map(|(x_chunk, y_chunk)| {
            let x_val = u64::from_ne_bytes(x_chunk.try_into().unwrap());
            let y_val = u64::from_ne_bytes(y_chunk.try_into().unwrap());
            (x_val ^ y_val).count_ones()
        })
        .sum::<u32>();
```

Another example is developing analog of `std::find`
[here](https://hackernoon.com/this-tiny-rust-tweak-makes-searching-a-slice-9x-faster):
branchless code
```
    for (i, &b) in haystack.iter().enumerate().rev() {
        if b == needle {
            position = Some(i);
        }
    }
```
fails to vectorize but `chunks_exact` helps:
```
fn find_no_early_returns(haystack: &[u8], needle: u8) -> Option<usize> {
    return haystack.iter().enumerate()
        .filter(|(_, &b)| b == needle)
        .rfold(None, |_, (i, _)| Some(i))
}

fn find(haystack: &[u8], needle: u8) -> Option<usize> {
    let chunks = haystack.chunks_exact(32);
    let remainder = chunks.remainder();
    chunks.enumerate()
        .find_map(|(i, chunk)| find_no_early_returns(chunk, needle).map(|x| 32 * i + x) )
        .or(find_no_early_returns(remainder, needle).map(|x| (haystack.len() & !0x1f) + x))
}
```
# TODO

- For all problematic features (e.g. bounds checks) collect how they influence autovec (via LLVM debug)
  * Done in [bounds checks analysis](../bounds/analysis.md)
- Check SLP vs loop autovec stats
  * Low prio
- Try autovec for simple ubenchmarks (DOALL, reduction, strlen)
  * DOALL and reductions vectorize fine, strlen-like loops are not vectorized neither in Rust, nor C
