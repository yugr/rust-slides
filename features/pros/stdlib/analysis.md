# Administrivia

Assignee: yugr

Parent task: gh-38

Effort: 0.5h

# Background

Some of algorithms and containers in Rust are more modern (and consequently faster)
than in C++.

Below we will cover the most known cases.

## Sorting

TODO:
  - algo differences
  - safety overheads in Rust
  - compare number of comparator calls (three-way comparison in Rust) ?

## Hashtable

TODO:
  - algo differences

## Search tree

TODO:
  - algo differences

# Optimizations

Algorithmic differences are too high-level for compiler to compensate for.

# Workarounds

C++ developers can use alternative implmentations from other libraries
(e.g. Abseil).

# Suggested reading

[Safety vs Performance. A case study of C, C++ and Rust sort implementations](https://github.com/Voultapher/sort-research-rs/blob/main/writeup/sort_safety/text.md)

# Performance impact

TODO:
  - minibenchmark results

### Runtime improvements

TODO:
  - compare against similar features in hardened C++
  - collect perf measurements for benchmarks:
    * runtime
      + large unexpected changes need to be investigated
    * code size (if applicable)
