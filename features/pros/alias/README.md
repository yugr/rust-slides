All info about alias analysis improvements in Rust.

Rust's reference semantics allows compiler to be much more aggressive
(we need to check whether it really is).

In particular:
  - mutable reference is guaranteed to be `noalias` (aka `restrict`)
  - shared references are guaranteed to point to immutable data
  - all references are guaranteed to be non-null
