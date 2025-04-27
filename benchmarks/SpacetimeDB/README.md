SpacetimeDB benchmarks are located in the `crates/bench` subdirectory of the [repo](https://github.com/clockworklabs/SpacetimeDB)

Built and tested on `69ec80331fe930c8c9160ab256b1858270d791ea` commit.

# Build

Built and tested with `rustc` version `rustc 1.84.0 (9fc6b4312 2025-01-07)` and `cargo` version `cargo 1.84.0 (66221abde 2024-11-19)`

- Install .NET SDK 8.0 (optional, only two benches will fail without it)

# Run

Change folder to `SpacetimeDB\crates\bench` and execute `cargo bench --bench generic --bench special --no-fail-fast` (approx 30m on x86 12-core machine to build and run the benchmarks)
