This is the plan for our work on the talk.
Project will be done in several phases outlined below.

# Survey of materials

This stage is about collection of relevant materials.

Methodology is available [here](materials/method.md) and
final results [here](materials/materials.md).

# Analysis of materials

This part is about analysis of [collected materials](materials/materials.md).

Methodology is available [here](features/method.md)
and results need to be stored in
  - [materials.md](materials/materials.md) (summary info about material)
  - [features/](features) (perf feature info extracted from material)

# Analysis of language perf features

This part is about analysis of Rust performance features (i.e. issues and opportunities).

Methodology is available [here](features/method.md)
and results need to be stored in [features/](features).

# Analysis of real code

This part consists of analysis of real-world performance-critical Rust projects.
It's not clear if we'll even get to this point but anyway here are some thoughts.

We could analyze
  - algorithms
    * CS 101 e.g. sorts/trees
    * math e.g. matmul/FFT
    * relatively easy to collect ([benchmarks game](https://benchmarksgame-team.pages.debian.net/benchmarksgame/measurements/rust.html))
  - real production code
    * very hard to analyze
      + need methodology (e.g. first profile and study only hotspots)
    * [candidates](real-projects.md)
