This file contains info about how to analyze language performance features
(i.e. issues and opportunities).

The essense of our talk is to
  - collect exhaustive list of language performance features
  - analyze each of them

The work consists of 2 parts:
  - preparing list of language features (based on collected materials)
  - for each feature, finding as much relevant info from public materials as possible (based on collected materials)
  - for each feature, manually research info that is missing

# Materials analysis

Before starting analysis of some material YOU MUST LOCK IT:
  * add annotation at particular item in [materials](../materials/materials.md):
```
Assignee: your-id
Status: in progress
```
  * commit and push this change (resolving conflicts if necessary)

For each piece of [materials](../materials/materials.md) (blog/forum post) we need to
  - carefully read/watch it
  - if material is in wrong section - move appropriately
  - for blogposts be sure to check
    * comments in blog itself and in its Reddit/Hackernews announcements :
      + Reddit: `TOPIC site:https://news.ycombinator.com`
      + HackerNews: `TOPIC site:https://news.ycombinator.com`
    * relevant links in text (need to be added to materials)
    * other Rust-performance-relevant posts on blog (posts which look relevant need to be added to materials)
    * for articles check "Related work"
  - for forum posts be sure to check
    * suggested posts (need to be added to materials)
  - write short summary (in [materials](../materials/materials.md)):
    * what was the problem(s) (e.g. "autovectorization breaks if indexing is too complex")
    * solution (e.g. "use unsafe" or "explicit SIMD")
    * results (e.g. "problem fully solved", "can not be solved in compiler", "should be worked around by user")
    * non-trivial conclusions (e.g. "never use XXX when YYY")
    * is it relevant for us and how (good code examples, good analysis, important optimization method/workaround, etc.) ?
  - if material is relevant:
    * add it to relevant feature file in [features/](/features)
    * add examples, methods, good citations
    * (create new directory if necessary)
  - mark very high quality/influential posts in dedicated section in [gems.md](../materials/gems.md)
    * e.g. with useful methodology, important ideas, good explanation of some subject, etc.
    * such posts MUST be read by all team members
    * such posts will be part of recommended readings

When commiting changes
  - change Status to DONE and add how much time you spent on it (to help with future planning)

# Research

For each performance feature we neeed to provide
  - why is this feature needed ?
    * example errors which are caught by this check
    * CVE/KEV stats:
      + CVE: https://github.com/CVEProject/cvelistV5
      + KEV: https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json
      + Mitre top-25 rating also considers severity: https://cwe.mitre.org/top25/archive/2024/2024_cwe_top25.html
    * enabled by default and why
    * situation in C++
  - clear example (Rust microbenchmark, asm code)
  - types of check (e.g. compiler/stdlib parts)
  - info whether LLVM can potentially optimize it (and with what limitations)
  - info on how developer can work around it and with how much effort/ugliness (unsafe, wrapping operations, reslicing, etc.)
    * pay special attention to cases which can not be optimized at all
  - links to important articles (design, etc.)
  - (need to collect prooflinks with timecodes, reprocases for everything)
  - performance impact:
    * is this check is a common case in practice ?
      * may need to write analysis passes to scan real Rust code (libs, big projects) for occurences
    * determine how to enable/disable feature in compiler/stdlib
      + there may be flags (e.g. for interger overflows) but sometimes may need patch code (e.g. for bounds checks)
        - patch for each feature needs to be implemented in separate branch (in private compiler repo)
        - compiler modifications need to be kept in private compiler repo `yugr/rust-private`
      + make sure that found solution works on real examples
      + note that simply using `RUSTFLAGS` isn't great because they override project settings in `Cargo.toml`
    * collect perf measurements for benchmarks:
      + runtime
      + PMU counters (inst count, I$/D$/branch misses)
        - actually we failed to understand how to collect PMUs in benchmarks (gh-25)...
      + compiler stats
        - depend on feature
        - e.g. SLP/loop autovec for bounds checking feature
        - e.g. NoAlias returns from AA manager for alias feature
        - e.g. CSE/GVN/LICM for alias feature
    * at least x86/AArch64
      + maybe also normal/ThinLTO/FatLTO, cgu=default/1 in future if we have time
  - fix all TODOs that are mentioned in feature's README

Hopefully in many cases all above will be obtained from collected materials.

# Priorities

Mandatory:
  - cons/abi and pros/abi (gh-31)
  - cons/arithmetic-checks (gh-28)
  - cons/autovec (gh-29)
  - cons/bounds-checks (gh-20)
  - cons/cgu (gh-30)
  - cons/copy-elision (gh-32)
  - cons/data-structs (gh-33)
  - cons/fastmath (gh-34)
  - cons/init (gh-35)
  - cons/panics (gh-36)
  - cons/placement-new (gh-37)
  - cons/stdlib and pros/stdlib (gh-38)
  - pros/alias (gh-39)

Important:
  - cons/iterators
  - cons/tls
  - pros/move
  - pros/inline
  - pros/likely
  - pros/niche
  - pros/noplt
  - pros/static
  - pros/visibility

Nice:
  - cons/other
  - cons/probestack
  - cons/size
  - pros/gc-sections
  - pros/long-indices
  - pros/other
  - pros/vtable
