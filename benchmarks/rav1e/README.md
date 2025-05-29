rav1e [repo](https://github.com/xiph/rav1e)

Built and tested on `6ee1f3a678deb9ccef2e3345168e39cd53e5d1a6` commit.

# Build

Built and tested with `rustc` version `rustc 1.86.0 (05f9846f8 2025-03-31)` and `cargo` version `cargo 1.86.0 (adf9b6ad1 2025-02-28)`

# Run

- Install nasm
- Run `cargo install cargo-criterion` to install criterion for running the benchmarks

Execute `cargo criterion --features=bench` (approx 70m on x86 12-core machine to build and run the benchmarks)
