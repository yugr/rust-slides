Rust adds safety checks for some arithmetic operations.
See [dedicated page](overflow-checks/README.md) for overflow checks.

Another example is division - as shown [here](https://codspeed.io/blog/why-rust-doesnt-need-a-standard-divrem#an-inline-assembly-version)
the overhead may be quite significant (7%).
There we check `x / 0` and `MIN / -1`.

# Solution

- Unchecked operations (see [here](https://codspeed.io/blog/why-rust-doesnt-need-a-standard-divrem#the-cost-of-panic-handling-an-unchecked-version))
- Special type `NonZeroU32`
- Asserts or `core::hint::unreachable_unchecked`

# TODO

- Benchmark without div check
- Detect all sources of panic in compiler (besides bounds checks)
  * Manually or using [no_panic crate](https://docs.rs/no-panic/latest/no_panic/)
