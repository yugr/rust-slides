Veloren [repo](https://github.com/veloren/veloren)

Built and tested on `8598d3d9c5c3a9e6d2366cfe882b479ce92a7bcc` commit (nightly).

# Build

Built and tested with `rustc` version `rustc 1.86.0-nightly (a567209da 2025-02-13)` and `cargo` version `cargo 1.86.0-nightly (2928e3273 2025-02-07)`

- Install `libxcbcommon-x11-dev`
- Try building with `cargo bench --jobs 1` if build failes on linking with OOM (15G RAM was not enough)
- Build takes approx 60m on x86 12-core machine to build and run the benchmarks

# Run

Execute `cargo bench` (approx 10m on x86 12-core machine to run the benchmarks)

