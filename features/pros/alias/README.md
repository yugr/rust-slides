All info about alias analysis improvements in Rust.

Rust's reference semantics allows compiler to be much more aggressive
(we need to check whether it really is).

In particular:
  - mutable reference is guaranteed to be `noalias` (aka `restrict`)
  - shared references are guaranteed to point to immutable data (and thus are different from C++ `const T &` !)
  - all references are guaranteed to be non-null

# Examples

- [Rust Optimizations That C++ Can't Do](https://robert.ocallahan.org/2017/04/rust-optimizations-that-c-cant-do_5.html)
- [slice::revswap](https://users.rust-lang.org/t/possible-rust-specific-optimizations/79895/5)

# Comparison to C++ restrict

Some people say that C++ `restrict` is equivalent and widely used but truth is that
> the high amount (?) of bugs regarding that functionality in LLVM expsoed by the Rust compilar
> is an indicator that it's not being widely used there, though
(from [Reddit](https://www.reddit.com/r/rust/comments/px72r1/comment/hem3qy8/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button), [HN](https://news.ycombinator.com/item?id=20944403#20949290) and [HN](https://news.ycombinator.com/item?id=20948546)).

# Links

Good summary from [HN](https://news.ycombinator.com/item?id=14042318):
  - "Alias analysis has been the holy grail of compiler development for a while. In C++ it's a global, imperfect, and expensive analysis. In Rust you get it for free."

# TODO

- Try disabling `noalias` hints via `-Zmutable-noalias=no` for large/performant codebases
