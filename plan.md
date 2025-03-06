This is the plan for our work on talk.

Project will be split to 3 phases:
  - analysis of [collected materials](materials/materials.md)
  - analysis of Rust performance features (issues and opportunities)
  - (if we have time in future) analysis of real-world projects

# Analysis of materials

For each blog/forum post in [materials.md](materials/materials.md) we need to
  - carefully read/watch it
  - if material is in wrong section - move appropriately
  - for blogposts be sure to check
    * comments (in blog itself and on its Reddit/Hackernews announcements if present)
    * relevant links in text (need to be added to materials)
    * other Rust-performance-relevant posts on blog (posts which look relevant need to be added to materials)
  - for forum posts be sure to check
    * suggested posts (need to be added to materials)
  - write short summary (in materials.md):
    * what was the problem(s) (e.g. "autovectorization breaks if indexing is too complex")
    * solution (e.g. "use unsafe" or "explicit SIMD")
    * results (e.g. "problem fully solved")
    * non-trivial conclusions (e.g. "never use XXX when YYY")
    * conclusion: is it relevant for us and how (good code examples, good analysis, important optimization method/workaround, etc.) ?
  - if material is relevant:
    * add it to relevant issue(s)/opportunity(ies) in plan.md
    * create new issue/opportunity if necessary
  - mark very high quality/influential posts
    * e.g. with useful methodology, additional suggestions, good explanation of some subject, etc.

# Analysis of language perf features

The essense of this talk is to
  - collect exhaustive list of performance issues/opportunities in Rust
  - analyze each issue/opportunity

To analyze, we need to
  - provide clear example (Rust microbenchmark, asm code)
  - analyze whether LLVM can potentially optimize it (and with what limitations)
  - analyze how developer can work around it and with how much effort/ugliness (unsafe, wrapping operations, reslicing, etc.)
    * pay special attention to cases which can not be optimized at all
  - determine whether this error is a common case in practice
    * may need to write analysis passes to scan real Rust code (libs, big projects) for occurences
  - (need to collect prooflinks with timecodes, reprocases for everything)

Hopefully in many cases all of the above will be obtained from collected materials.
But in some cases we will need to make our own analysis:
  - prepare reasonable microbenchmarks
  - TODO

# Analysis of real code

It's not clear if we'll even get to this point but anyway here are some thoughts.

We could analyze
  - algorithms
    * CS 101 e.g. sorts/trees
    * math e.g. matmul/FFT
    * relatively easy to collect ([benchmarks game](https://benchmarksgame-team.pages.debian.net/benchmarksgame/measurements/rust.html))
  - real production code
    * very hard to analyze
      + need methodology (e.g. first profile and study only hotspots)
    * concrete examples:
      * Eigen vs nalgebra
      * [other projects](real-projects.md)
