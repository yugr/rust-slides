Various leftover performance issues which are too niche to get dedicated slot.

Rust misses some very low-level C/C++ features:
  - computed goto
  - `alloca`
  - guarantted tailcall elimination

# Guarantteed tailcalls

Rust compiler, like Clang, may support TCO via LLVM optimizer.

But guaranteed tailcall elimination, like Clang's `musttail`, is not available.

RFC for explicit tail calls with `become` keyword is [in development](https://github.com/rust-lang/rfcs/pull/3407/files).

Some crates (tco, tramp) provide macros that perform tail call optimization, however they are not in a good state (only POC or without actual zero-cost tail calls).
