Various leftover performance issues which are too niche to get dedicated slot.

Rust doesn't have TCO (yet).
RFC for explicit tail calls with `become` keyword is in development.
Some crates (tco, tramp) provide macros that perform tail call optimization, however they are not in a good state (only POC or without actual zero-cost tail calls).

Rust misses some very low-level C/C++ features:
  - computed goto
  - `alloca`
