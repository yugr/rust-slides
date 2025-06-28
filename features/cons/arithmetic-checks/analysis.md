# Administrivia

Assignee: yugr
Parent task: gh-28
Effort: 1h

# Background

TODO:
  - why is this feature needed ?
    * example errors
    * CVE stats (for CWEs from https://cwe.mitre.org/data/definitions/189.html)
    * situation in C++
  - types of checks (f2i/integer-overflow/divide-by-zero, compiler instrumention, checks in stdlib containers, lack of `nsw` annotations in compiler)
  - why is this feature not enabled by default ?
  - fix all TODOs that are mentioned in feature's README

# Examples

TODO:
  - clear example (Rust microbenchmark, asm code)

# Optimizations

TODO:
  - info whether LLVM can potentially optimize it (and with what limitations)

# Workarounds for bounds checks

TODO:
  - how developer can work around it and with how much effort/ugliness (unsafe, wrapping operations, reslicing, etc.)
    * pay special attention to cases which can not be optimized at all

# Suggested reading

TODO:
  - links to important articles (design, etc.)

# Performance impact

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
