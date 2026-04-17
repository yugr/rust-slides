Oxipng [repo](https://github.com/shssoichiro/oxipng)

Build and tested on `788997c437319995e55030a92ed8294dfcd4c87a` commit.

Oxipng is extremely sensitive to code layouts
(i.e. linker and library versions, unrelated opts, etc.),
likely due to very short hot loops.

# Build

Built and tested with `rustc` version `rustc 1.85.0-nightly (d117b7f21 2024-12-31)` (stable) and `cargo` version `cargo 1.85.0-nightly (c86f4b3a1 2024-12-24)`

- Copy `rust-toolchain.toml` file into the repository to choose nightly toolchain version (doesn't build otherwise)

# Run

Execute `cargo bench` (approx 40m on x86 12-core machine to build and run the benchmarks)
