Meilisearch benchmarks are located in the `crates/benchmarks` subdirectory of the [repo](https://github.com/meilisearch/meilisearch)

Built and tested on `0fd66a5317da7e1f075058665944cac62e17d446` commit.

# Build

Built and tested with `rustc` version `rustc 1.85.1 (4eb161250 2025-03-15)` and `cargo` version `cargo 1.85.1 (d73d2caf9 2024-12-31)`.

# Run

Change folder to `meilisearch/crates/benchmarks` and execute `cargo bench` (approx 95m for building and running benchmarks on x86 12-core machine, most of the time are benchmarks themselves)

# Bench

When running benchmarks it's useful to specify
```
export MEILI_MAX_INDEXING_THREADS=1 RAYON_NUM_THREADS=1
```
Also useful to remove unnecessary queries in `BASE_CONF` and `confs` variables.
