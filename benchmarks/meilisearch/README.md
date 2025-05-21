Meilisearch benchmarks are located in the `crates/benchmarks` subdirectory of the [repo](https://github.com/meilisearch/meilisearch)

Built and tested on `8a0bf24ed5c0b49cb788a57ac19eaa43076962bf` commit.

# Build

Built and tested with `rustc` version `rustc 1.85.1 (4eb161250 2025-03-15)` and `cargo` version `cargo 1.85.1 (d73d2caf9 2024-12-31)`.

# Run

Change folder to `meilisearch/crates/benchmarks` and execute `cargo bench` (approx 95m for building and running benchmarks on x86 12-core machine, most of the time are benchmarks themselves)
