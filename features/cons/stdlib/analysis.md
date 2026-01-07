# Administrivia

Assignee: yugr

Parent task: gh-38

Effort: 0h

TODO: fix all TODOs that are mentioned in feature's README

# Background

TODO:
  - why these features are needed ?
    * example errors which are caught by this check
    * CVE/KEV stats:
      + CVE: https://github.com/CVEProject/cvelistV5
      + KEV: https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json
      + Mitre top-25 rating also considers severity: https://cwe.mitre.org/top25/archive/2024/2024_cwe_top25.html
    * enabled by default and why
    * situation in C/C++
      + e.g. [The New C Standard: An Economic and Cultural Commentary](https://www.coding-guidelines.com/cbook/cbook1_1.pdf)
      + e.g. [Rationale for International Standard Programming Languages - C](https://www.open-std.org/jtc1/sc22/wg14/www/C99RationaleV5.10.pdf)
    * situation in other langs:
      + [Java](https://docs.oracle.com/javase/specs/jls/se24/html/),
      + [C#](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/language-specification/introduction)
      + [Go](https://go.dev/ref/spec)
      + [Swift](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/aboutthelanguagereference/)
      + [Fortran](https://j3-fortran.org/doc/year/24/24-007.pdf)
      + Ada ([RM](http://www.ada-auth.org/standards/22rm/html/RM-TOC.html) and [ARM](http://www.ada-auth.org/standards/22aarm/html/AA-TOC.html))
  - types of check (e.g. compiler/stdlib parts)

# Examples

TODO:
  - clear examples (Rust microbenchmark, asm code)

# Optimizations

TODO:
  - info whether LLVM and MIR opts can potentially optimize it (and with what limitations)

# Workarounds

TODO:
  - info on how developer can work around it and with how much effort/ugliness (unsafe, wrapping operations, reslicing, etc.)
    * pay special attention to cases which can not be optimized at all

# Suggested reading

TODO:
  - links to important articles (design, etc.)
  - (need to collect prooflinks with timecodes, reprocases for everything)

# Performance impact

## Prevalence

TODO:
  - is this check is a common case in practice ?
    * may need to write analysis passes to scan real Rust code (libs, big projects) for occurences

## Measurements

TODO:
  - determine how to enable/disable feature in compiler/stdlib
    * there may be flags (e.g. for interger overflows) but sometimes may need patch code (e.g. for bounds checks)
      + patch for each feature needs to be implemented in separate branch (in private compiler repo)
      + compiler modifications need to be kept in private compiler repo `yugr/rust-private`
    * make sure that found solution works on real examples
    * note that simply using `RUSTFLAGS` isn't great because they override project settings in `Cargo.toml`

### Static estimates

TODO:
  - compiler stats
    * depend on feature
    * LLVM stats may be misleading because some opts (e.g. inline) are done in frontend
      (at MIR level). But recollecting with `-Zmir-opt-level=0`
      e.g. in panic feature didn't improve anything.
    * e.g. SLP/loop autovec for bounds checking feature
    * e.g. NoAlias returns from AA manager for alias feature
    * e.g. CSE/GVN/LICM for alias feature

### Runtime improvements

TODO:
  - compare against similar features in hardened C++
  - collect perf measurements for benchmarks:
    * runtime
      + large unexpected changes need to be investigated
    * code size (if applicable)
