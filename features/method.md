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

For each piece of [materials](materials/materials.md) (blog/forum post) we need to
  - carefully read/watch it
  - if material is in wrong section - move appropriately
  - for blogposts be sure to check
    * comments (in blog itself and on its Reddit/Hackernews announcements if present)
    * relevant links in text (need to be added to materials)
    * other Rust-performance-relevant posts on blog (posts which look relevant need to be added to materials)
  - for forum posts be sure to check
    * suggested posts (need to be added to materials)
  - write short summary (in [materials](materials/materials.md)):
    * what was the problem(s) (e.g. "autovectorization breaks if indexing is too complex")
    * solution (e.g. "use unsafe" or "explicit SIMD")
    * results (e.g. "problem fully solved")
    * non-trivial conclusions (e.g. "never use XXX when YYY")
    * is it relevant for us and how (good code examples, good analysis, important optimization method/workaround, etc.) ?
  - if material is relevant:
    * add it to relevant feature file in [features/](features)
    * (create new file if necessary)
  - mark very high quality/influential posts in dedicated section in [gems.md](materials/gems.md)
    * e.g. with useful methodology, important ideas, good explanation of some subject, etc.
    * such posts MUST be read by all team members

# Research

Each performance feature neeeds to contain
  - clear example (Rust microbenchmark, asm code)
  - info whether LLVM can potentially optimize it (and with what limitations)
  - info on how developer can work around it and with how much effort/ugliness (unsafe, wrapping operations, reslicing, etc.)
    * pay special attention to cases which can not be optimized at all
  - info on whether this error is a common case in practice
    * may need to write analysis passes to scan real Rust code (libs, big projects) for occurences
  - (need to collect prooflinks with timecodes, reprocases for everything)

Hopefully in many cases all above will be obtained from collected materials.
But in some cases we will need to make our own analysis:
  - prepare reasonable microbenchmarks
  - collect statistics for real-world code (via LLVM/asm analysis) if some safety feature is disabled
  - TODO
