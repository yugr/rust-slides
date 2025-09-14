# Administrivia

Assignee: yugr

Parent task: gh-28

# Background

This feature is an umbrella for various arithmetic operations checks in Rust:
  - division checks
    * divide-by-zero and division overflow (`INT_MIN / -1`, signed types only)
    * enabled by default and no flag to control this
    * implemented in codegen
  - type conversions
    * f2i conversions are saturating
    * enabled by default and can be disabled with `-Zsaturating-float-casts=off`
    * implemented in codegen
  - integer overflows (arithmetic and shifts)
    * disabled by default and can be enabled with `-C overflow-checks=on`
    * effectively UB: panic in debug, wrap in release
    * overhead in release due to missing `nsw`
    * implemented in codegen
    * strangely overflow in division (`INT_MIN / -1` is checked unconditionally)
  - size overflows in containers
    * enabled by default
    * implemented in stdlib code (`checked_add`, `checked_sub`, `Layout` class checks, etc.)

Some naturally expected checks on the other hand are missing:
  - type conversions are particularly incomplete:
    * `as` does not check overflow at all
    * `into()` needs to be explicit

Different defaults are weird and mainly driven by performance costs.
Rust developers clearly [state](https://github.com/rust-lang/rfcs/pull/560#issuecomment-69403142) that
> Plan is to turn on checking by default if we can get the performance hit low enough
and also that it should
> leave room in the future to move towards universal overflow checking if it becomes feasible
and also [here](https://www.reddit.com/r/rust/comments/4gz93u/comment/d2mcoje/)
> It is hoped that as the performance of checks improves (notably with delayed checks, better value propagation, etc...),
> at some point in the future they could be switched on by default.
and [here](https://internals.rust-lang.org/t/question-why-does-dividing-by-zero-have-no-safety-guarantees/19189/3):
> When it comes to basic arithmetic, Rust chose performance and convenience over strict correctness,
> so, for example, addition does not return a Result even though it's a partial function (it may overflow).
> And it doesn't even panic by default in release mode but wraps around instead (so directly maps to hardware addition).

C++ also has mechanisms to catch overflows and
they are sometimes enabled even in production code (see [README](overflow-checks/README.md)).

2024 CVE stats: 299 out of total 33k i.e. 1%.
This is more than 10x less than memory errors which explains why overflow checks are disabled by default.

2024 KEV stats: 3 out of total 181 i.e. 1.5% (4x less than buffer overflow errors).
```
$ CVE/kev_scanner.py -y 2024 known_exploited_vulnerabilities.json
3 Integer Overflow
12 Memory Overflow
0 Stack overflow
0 Uninitialized
181 Total
```

[Mitre 2024 top-25 weaknesses rating](https://cwe.mitre.org/top25/archive/2024/2024_cwe_top25.html):
integer overflow is no. 23 and NULL deref no. 21.

Some very famous SW errors were caused by integer overflow:
  - Therac-25 incident (1985)
  - Ariane 5 crash (1996)

TODO:
  - situation in other langs

# Examples

This simple program
```
#[no_mangle]
pub fn foo(xs: &[i32]) -> i32 {
    let mut ans = 0;
    for x in xs {
        ans += x;
    }
    ans
}
```
vectorizes well by default
```
$ rustc --crate-type=rlib --emit=asm -o- -C target-cpu=native -O repro.rs
...
.LBB0_10:
        vpaddd  (%rdi,%rax,4), %ymm0, %ymm0
        vpaddd  32(%rdi,%rax,4), %ymm1, %ymm1
        vpaddd  64(%rdi,%rax,4), %ymm2, %ymm2
        vpaddd  96(%rdi,%rax,4), %ymm3, %ymm3
        addq    $32, %rax
        cmpq    %rax, %r8
        jne     .LBB0_10
...
```
but breaks when overflows are enabled:
```
$ rustc ... -C overflow-checks=on
...
.LBB0_3:
        addl    (%rdi,%rcx), %eax
        jo      .LBB0_6
        addq    $4, %rcx
        cmpq    %rcx, %rsi
        jne     .LBB0_3
...
```

# Optimizations

In theory LLVM could still vectorize in presence of overflow checks
by vectorizing the overflow checks itself but this is currently not done.

Also multiple successive checks could be combined
(so called [delayed panics](https://github.com/rust-lang/rfcs/blob/master/text/0560-integer-overflow.md#delayed-panics))
e.g. here
```
fn foo(mut x: i32, y: i32) -> i32 {
  x += y;
  x += y;
  x
}
```
but it's not done.

TODO:
  - why they are not used by LLVM optimizer

To check how many overflow checks are optimized by LLVM
we count panics in initial IR vs optimized IR.

Checks in unoptimized IR:
```
$ RUSTFLAGS_NOT_BOOTSTRAP='-Csave-temps -Coverflow-checks=on' ./x build --stage 2 compiler
$ find build/x86_64-unknown-linux-gnu/{stage1-std,stage1-rustc} -name '*.no-opt.bc' \
  | xargs ~/tasks/rust/count-overflow-panics/Count \
  | awk 'BEGIN{s=0} {s+=$2} END{print s}'
70947
```

Checks in optimized IR:
```
$ for bc in `fn build/x86_64-unknown-linux-gnu/{stage1-std,stage1-rustc} *.no-opt.bc`; do
  /home/yugr/src/rust/rust/build/x86_64-unknown-linux-gnu/ci-llvm/bin/opt -O2 -disable-loop-unrolling -vectorize-loops=false -vectorize-slp=false $bc -o tmp.bc
  ~/tasks/rust/count-overflow-panics/Count tmp.bc
done | awk 'BEGIN{s=0} {s+=$2} END{print s}'
38915
```
So 45% of checks are optimized by LLVM !

Better yet, also remove inline - use
```
$ /home/yugr/src/rust/rust/build/x86_64-unknown-linux-gnu/ci-llvm/bin/opt -O2 -print-pipeline-passes /dev/null
```
to extract `-O2` pipeline and remove inline, loop-vectorize, slp-vectorize and unroll passes.
With this, I get
```
44133
```

But this may be misleading because most checks are trivially optimizable:
```
$ for bc in `fn build/x86_64-unknown-linux-gnu/{stage1-std,stage1-rustc} *.no-opt.bc`; do
  /home/yugr/src/rust/rust/build/x86_64-unknown-linux-gnu/ci-llvm/bin/opt -passes='mem2reg,sroa<preserve-cfg>,instcombine<max-iterations=100>' $bc -o tmp.bc
  ~/tasks/rust/count-overflow-panics/Count tmp.bc
done | awk 'BEGIN{s=0} {s+=$2} END{print s}'
49354
```
So just 21% of checks are not super-trivial.
early-cse<>, gvn<>, adce, bdce, instsimplify, sccp and correlated-propagation are responsible for the rest.

# Workarounds for overflow checks

Overflow checks are already covered [here](overflow-checks/README.md#solutions).

Division-by-zero checks can be avoided with
  - using `NonZeroU32` type wrapper

f2i saturating checks can be avoided with
  - `to_int_unchecked`

Overflow checks in containers can't be worked around.

# Suggested reading

[Myths and Legends about Integer Overflow in Rust](https://huonw.github.io/blog/2016/04/myths-and-legends-about-integer-overflow-in-rust)
  - survey of RFC 560

[Understanding Integer Overflow in C/C++](https://users.cs.utah.edu/~regehr/papers/overflow12.pdf)
  - paper by John Regehr

# Performance impact

John Regehr's well known study [estimates](https://users.cs.utah.edu/~regehr/papers/overflow12.pdf)
integer checks to have 30-50% overhead on average (with up to 3x worst case).
He also argues that HW support for overflow checking would significantly reduce costs.
But some arhictects [claim](https://news.ycombinator.com/item?id=8766264) that
this will cause a big (~5%) increase of clock cycle.
Dan Luu is more positive, with [few percent](http://danluu.com/integer-overflow/) estimate.

[Our studies](https://github.com/yugr/slides/blob/main/CppZeroCost/2025/plan.md)
also show ~30% overhead in Clang.

Overflow checks hurt performance in three ways:
  - overhead to do the checks
  - cache pressure (I$, BTB)
  - inhibiting other opts (e.g. autovec) due to more complex control flow and
    [broken SCEV analysis](https://kristerw.blogspot.com/2016/02/how-undefined-signed-overflow-enables.html)

## Prevalence

I used the same approach as outlined in [bounds checking](../bounds-checks/analysis.md#overall-panics).

Relevant panics seem to be
```
# Default
core::slice::index::slice_start_index_overflow_fail
core::panicking::panic_const::panic_const_div_overflow
core::slice::index::slice_end_index_overflow_fail

# Forced
core::panicking::panic_const::panic_const_neg_overflow
core::panicking::panic_const::panic_const_shr_overflow
core::panicking::panic_const::panic_const_shl_overflow
core::panicking::panic_const::panic_const_mul_overflow
core::panicking::panic_const::panic_const_sub_overflow
core::panicking::panic_const::panic_const_add_overflow
```

Results for rustc:
  - (A) 430214
  - (A+) not relevant
  - (B) 429725
    * not sure how it's smaller than (A)...
  - (Z) 472510 (+10% compared to default, 9% of panics are overflows)
    * needed to enable overflow checks explicitly:
      ```
      [rust]
      overflow-checks = true
      ```

## Disabling the check

Default Rust is a middle-ground - it enables _some_ arithmetic checks but not all of them.
Disabling default checks is impossible, extraneous checks may be enabled with `-C overflow-checks=on`.

## Measurements

As discussed we have three variants to test:
  - (A) all arithmetic checks removed ([yugr/no-overflow-checks/1](https://github.com/yugr/rust-private/tree/yugr/no-overflow-checks/1) branch)
    * note that explicit `checked_add`, etc. were preserved (I only removed them from stdlib)
    * `strict_add` family from stdlib wasn't changed either (because they don't seem to be widely used)
  - (A+) same as (A) but also add nsw markers in LLVM IR (to match C signed overflow semantics, [yugr/no-overflow-checks-nsw/2](https://github.com/yugr/rust-private/tree/yugr/no-overflow-checks-nsw/2) branch)
  - (B) default ([yugr/baseline](https://github.com/yugr/rust-private/tree/yugr/baseline) branch)
  - (Z) all arithmetic checks enabled ([yugr/force-overflow-checks/1](https://github.com/yugr/rust-private/tree/yugr/force-overflow-checks/1) branch)

For (A) there are some limitations:
  - I only disabled low hanging fruits i.e. places where checks were in nearby code
  - I didn't modify internal stdlib APIs
    - e.g. didn't modify functions that return `Option` or `Result` (hoping that compiler will be able to optimize them out)
    + e.g. didn't modify checks in `size_hint` methods
  - I didn't disable alignment checks (e.g. in `Layout`)

### Static estimates

TODO: figure out what optimizations may get hurt due to this and measure this

### Runtime improvements

Disabling all checks obviously increases perf:
```
$ ../../benchmarks/compare.py baseline/ no-overflow-checks
compare.py: warning: some results are present only in /home/Asus/src/rust-slides/tmp/results-20250826/baseline: meilisearch_0.json
SpacetimeDB_0.json: +1.5%
bevy_0.json: +0.6%
meilisearch_0.json: +0.0%
nalgebra_0.json: +0.3%
oxipng_0.json: +0.2%
rav1e_0.json: +2.2%
regex_0.json: +0.4%
ruff_0.json: +0.9%
rust_serialization_benchmark_0.json: -0.1%
tokio_0.json: +0.2%
uv_0.json: -0.3%
veloren_0.json: +1.5%
zed_0.json: +0.3%
```

On the other hand enforcing them clearly decreases it A LOT:
```
$ ../../benchmarks/compare.py baseline/ force-overflow-checks/
compare.py: warning: some results are present only in /home/Asus/src/rust-slides/tmp/results-20250826/baseline: meilisearch_0.json, rav1e_0.json, rust_serialization_benchmark_0.json
SpacetimeDB_0.json: -6.5%
bevy_0.json: -6.6%
meilisearch_0.json: -5.6%
nalgebra_0.json: -6.8%
oxipng_0.json: -8.0%
regex_0.json: -0.9%
ruff_0.json: -0.8%
tokio_0.json: -1.4%
uv_0.json: -1.0%
veloren_0.json: -14.3%
zed_0.json: -10.5%
```
(rust_serialization_benchmark and rav1e crash with checks enabled).

NSW is not clearly better:
```
$ ../../benchmarks/compare.py no-overflow-checks no-overflow-checks-nsw/
SpacetimeDB_0.json: +0.3%
bevy_0.json: +0.1%
meilisearch_0.json: +0.3%
nalgebra_0.json: +0.1%
oxipng_0.json: -0.1%
rav1e_0.json: -2.2% (irrelevant because has overflows)
regex_0.json: -0.1%
ruff_0.json: +0.1%
rust_serialization_benchmark_0.json: -0.2% (irrelevant because has overflows)
tokio_0.json: +0.0%
uv_0.json: +0.0%
veloren_0.json: -1.4%
zed_0.json: -0.5%
```

TODO:
  - investigate regression in veloren (and zed ?)
  - perf measurements for AArch64
