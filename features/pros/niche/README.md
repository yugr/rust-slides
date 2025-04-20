All info about Rust's optimizations of structs and enums.

Rust may rearrange struct fields to minimize padding.

Rust may reuse empty bits for enum discriminator
(transparent pointer tagging vs fat pointers).
So `Option` can be optimized better than `std::optional`.
Two types of optimization:
  - Null pointer optimization
  - Niche filling

Unfortunately `Option<i32>` can't be optimized by compiler
and we can't tell convey this info to it in situations
where it's valid. Can use `Option<NonZeroU32>`:
> This enables some memory layout optimization.
> For example, Option<NonZeroU32> is the same size as u32 

# TODO

- Benchmark some big/performance critical project w/o niche opts (check Rss, cache, wall time)
