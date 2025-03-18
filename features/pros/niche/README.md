All info about Rust's optimizations of structs and enums.

Rust may rearrange struct fields to minimize padding.

Rust may reuse empty bits for enum discriminator.

# TODO

- Benchmark some big/performance critical project w/o niche opts (check Rss, cache, wall time)
