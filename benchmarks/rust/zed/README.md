There are two crates with benchmarks in zed [repository](https://github.com/zed-industries/zed), `crates/rope` and `crates/extension_host`.

Built and tested on `83d513aef48f6b4b56bad96740a02f5ef86a0a8c` commit.

# Build

Built and tested with `rustc` version `rustc 1.87.0 (17067e9ac 2025-05-09` and `cargo` version `cargo 1.87.0 (99624be96 2025-05-06)`.

- Install required dependencies by running `script/linux` script

# Run

Change folder to `zed/crates/rope` `zed/crates/extension_host` and execute `cargo bench` (approx 5.5m for building and running 15 benchmarks in `rope` and 5.5m more for one benchmark in `extension_host` on x86 12-core machine)
