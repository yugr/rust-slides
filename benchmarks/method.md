# Goal

We need to find a list of benchmarks which
  - are alive
  - cover broad spectrum of domains (games, browsers, linear algebra, etc.)
  - are relatively cheap to build and run (< 1h)
  - what else ???

# Search

We already have a list of [real-world projects and popular crates](../real-projects.md)
which will serve as a starting point.

This can be extended later by checking
  - most popular projects at https://crates.io/
  - [Awesome Rust](https://github.com/rust-unofficial/awesome-rust)

# Benchmark analysis

Each benchmark needs to be added in dedicated subfolder.

We need at least the following information:
  - how to build
  - how to run benches
  - additional (non-Rust) dependencies or system setup needed
  - what else ???

# Running benchmarks

Benchmarks need to run via standard approach
```
taskset 0x1 nice -n -20 setarch -R ...
```

# TODO

Do we need some standard Rust crate to run benchmarks ?
