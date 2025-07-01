TODO:
  - double-check materials for this feature
  - fix all TODOs that are mentioned in feature's README

# Administrivia

Assignee: yugr
Parent task: gh-28
Effort: 1h

# Background

This feature is an umbreally for various arithmetic operations checks in Rust:
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
    * implemented in stdlib code

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

2024 CVE stats: 274 out of total 33k i.e. 1%.
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

TODO:
  - why is this feature needed ?
    * example errors

# Examples

TODO:
  - clear example (Rust microbenchmark, asm code)

# Optimizations

TODO:
  - info whether LLVM can potentially optimize it (and with what limitations)

# Workarounds for bounds checks

Overflow checks are already covered [here](overflow-checks/README.md#solutions).

Division-by-zero checks can be avoided with
  - using `NonZeroU32` type wrapper

f2i saturating checks can be avoided with
  - `to_int_unchecked`

Overflow checks in containers can't be worked around.

# Suggested reading

TODO:
  - links to important articles (design, etc.)

# Performance impact

John Regehr's well known study [estimates](https://users.cs.utah.edu/~regehr/papers/overflow12.pdf)
integer checks to have 30-50% overhead on average (with up to 3x worst case).
He also argues that HW support for overflow checking would significantly reduce costs.
But some arhictects [claim](https://news.ycombinator.com/item?id=8766264) that
this will cause a big (~5%) increase of clock cycle.
Dan Luu is more positive, with [few percent](http://danluu.com/integer-overflow/) estimate.

Overflow checks hurt performance in three ways:
  - overhead to do the checks
  - cache pressure (I$, BTB)
  - inhibiting other opts (e.g. autovec) due to more complex control flow and broken SCEV analysis

## Prevalence

TODO:
  - is this check is a common case in practice ?
  - may need to write analysis passes to scan real Rust code (libs, big projects) for occurences

## Disabling the check

TODO:
  - determine how to enable/disable feature in compiler/stdlib
    * there may be flags (e.g. for interger overflows) but sometimes may need patch code (e.g. for bounds checks)
      + patch for each feature needs to be implemented in separate branch (in private compiler repo)
    * make sure that found solution works on real examples
    * note that simply using `RUSTFLAGS` isn't great because they override project settings in `Cargo.toml`
    * compiler modifications need to be kept in private compiler repo `yugr/rust-private`

## Measurements

### Static estimates

TODO:
  - compiler stats
    * depend on feature
    * e.g. SLP/loop autovec for bounds checking feature
    * e.g. NoAlias returns from AA manager for alias feature
    * e.g. CSE/GVN/LICM for alias feature

### Runtime improvements

TODO:
  - collect perf measurements for benchmarks:
    + runtime
    + PMU counters (inst count, I$/D$/branch misses)
    * x86/AArch64, normal/ThinLTO/FatLTO, cgu=default/1
