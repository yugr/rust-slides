# Administrivia

Assignee: yugr
Parent task: gh-39
Effort: 1h

TODO:
  - fix all TODOs that are mentioned in feature's README

# Background

TODO:
  - why is this feature needed ? (most runtime aliases are fake)
  - enabled by default and why
  - situation in C++
    * e.g. [The New C Standard: An Economic and Cultural Commentary](https://www.coding-guidelines.com/cbook/cbook1_1.pdf)
    * e.g. [Rationale for International Standard Programming Languages - C](https://www.open-std.org/jtc1/sc22/wg14/www/C99RationaleV5.10.pdf)
    * Rust vs. C type aliasing (too error-prone ?)
  - situation with raw pointers (no type aliasing rules => very conservative)
  - alias (pointer) analysis precision:
    * [AN EMPIRICAL STUDY OF ALIAS ANALYSIS TECHNIQUES](https://digitalcommons.calpoly.edu/cgi/viewcontent.cgi?article=3206&context=theses)
    * [Speculative Alias Analysis for Executable Code](https://arcb.csc.ncsu.edu/~mueller/pact02/papers/fernandez152.pdf):
      significant improvement of precision from using speculation

# Examples

TODO:
  - example codes which are optimized
  - clear example (Rust microbenchmark, asm code)

# Optimizations

TODO:
  - how LLVM can use this info (and with what limitations e.g. only function params)
    * [relevant paper](https://www.cs.utexas.edu/~mckinley/papers/alias-cc-2004.pdf)

# Suggested readings

TODO:
  - links to important articles (design, etc.)

# Performance impact

TODO:
  - is this optimization is a common case in practice ?
    * may need to write analysis passes to scan real Rust code (libs, big projects) for occurences
  - determine how to enable/disable feature in compiler/stdlib
    * there may be flags (e.g. for interger overflows) but sometimes may need patch code (e.g. for bounds checks)
      - patch for each feature needs to be implemented in separate branch (in private compiler repo)
      - compiler modifications need to be kept in private compiler repo `yugr/rust-private`
    * make sure that found solution works on real examples
    * note that simply using `RUSTFLAGS` isn't great because they override project settings in `Cargo.toml`

## Prevalence

TODO:
  - NoAlias returns from AA manager

## Measurements

### Static estimates

TODO:
  - collect compiler stats: SLP and loop autovec, CSE, GVN, LICM

### Runtime improvements

Disabling the feature obviously decreases perf:
```
$ ../../benchmarks/compare.py baseline/ force-aliasing/
compare.py: warning: some results are present only in /home/Asus/src/rust-slides/tmp/results-20250826/baseline: meilisearch_0.json, veloren_0.json
SpacetimeDB_0.json: -0.7%
bevy_0.json: -0.1%
nalgebra_0.json: -4.5%
oxipng_0.json: +2.1%
rav1e_0.json: -1.0%
regex_0.json: -1.2%
ruff_0.json: -1.1%
rust_serialization_benchmark_0.json: -1.9%
tokio_0.json: -0.4%
uv_0.json: -1.0%
zed_0.json: -1.2%
```

TODO:
  - investigate regression in oxipng
  - perf measurements for AArch64
