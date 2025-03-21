All info about alias analysis improvements in Rust.

Rust's reference semantics allows compiler to be much more aggressive
(we need to check whether it really is).

In particular:
  - mutable reference is guaranteed to be `noalias` (aka `restrict`)
  - shared references are guaranteed to point to immutable data
  - all references are guaranteed to be non-null

Some examples of this:
  - [Rust Optimizations That C++ Can't Do](https://robert.ocallahan.org/2017/04/rust-optimizations-that-c-cant-do_5.html)

Good summary from [HN](https://news.ycombinator.com/item?id=14042318):
  - "Alias analysis has been the holy grail of compiler development for a while. In C++ it's a global, imperfect, and expensive analysis. In Rust you get it for free."
