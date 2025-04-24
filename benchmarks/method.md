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
  - unusual compile flags in Cargo.toml (`panic=abort`, etc.)
  - what else ???

# Building benchmarks

Make sure that incremental compilation is not used after changes
(by removing build dir or using `export CARGO_INCREMENTAL=0`).

# Running benchmarks

Benchmarks need to run via standard approach
```
taskset 0x1 nice -n -20 setarch -R ...
```

Standard Rust benchmarks can be run using `cargo bench` command. Depending on benchmark implementation, it automatically warms up for 3s before benchmarking and runs each benchmark for approximately 5s. Low, mean and high time is reported, as well as number and type of outliers. It also can record benchmarking result and report change.

`cargo bench` does not seem to alter benchmarking process schedaffinity or niceness, so the preferred method of running `cargo bench` is
```
sudo renice -n -20 $$
taskset 0x1 setarch -R cargo bench
```
(what abour multithreaded benchmarks though ?).

Also we may need to
  - boot to non-GUI mode (low runlevel) on systemd systems (https://linuxconfig.org/how-to-disable-enable-gui-in-ubuntu-22-04-jammy-jellyfish-linux-desktop)
  - use `isolcpus`/`nohz_full` kernel boot flags
  - fix CPU frequency (in BIOS or, if not available, by setting `scaling_governor` to `performance`)
  - disable HW prefetching in BIOS

# Common benchmarking tools

Most popular Rust benchmarking crate is the `Criterion.rs` crate. Nightly version of Rust also has built-in `[#bench]` attribute. There also may be other benchmarking frameworks, but for a well-structured crate cargo should provide a simple `cargo bench` abstraction that will run all the available benchmarks (and tests) automatically.
