Ruff benchmarks are located in the `crates/ruff_benchmark` subdirectory of the [repo](https://github.com/astral-sh/ruff)

Built and tested on `b302d89da3325c705f87a8343a16aad1723b67ab` commit.

# Build

Built and tested with `rustc` version `rustc 1.87.0 (17067e9ac 2025-05-09)` and `cargo` version `cargo 1.87.0 (99624be96 2025-05-06)`.

# Run

Change folder to `ruff/crates/ruff_benchmark` and execute `cargo bench` (approx 7m for building and running benchmarks on x86 12-core machine)
