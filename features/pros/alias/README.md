All info about alias analysis improvements in Rust.

Rust's reference semantics allows compiler to be much more aggressive
(we need to check whether it really is).

In particular:
  - mutable reference is guaranteed to be `noalias` (aka `restrict`)
  - shared references are guaranteed to point to immutable data (and thus are different from C++ `const T &` !)
  - all references are guaranteed to be non-null

Important note: prefer to use (e.g. pass to functions) `&[T]` instead of `&Vec<T>`
(as LLVM [can optimize the former better](https://users.rust-lang.org/t/rust-program-has-only-42-the-speed-of-similar-c-program/73738/24)).

Note that aliasing optimizations are NOT applied to pointers.
Moreover, Rust does not have any kind of strict aliasing so
`*mut i32` and `*mut f32` may alias.
So using raw pointers has a performance hit compared to C++.

Note that aggressive noaliasing is also the main reason
for high performance of Fortran.

# Problems

Alias info is not propagated to LLVM in all possible cases due to limitations of LLVM IR
(see e.g. [this case](https://blog.polybdenum.com/2017/02/19/how-copying-an-int-made-my-code-11-times-faster.html)).

In [some cases](https://github.com/rust-lang/rust/commit/71f5cfb21f3fd2f1740bced061c66ff112fec259)
people even pass references to dummy functions to force LLVM noalias annotations on them
to promote optimization.

# Examples

- [Rust Optimizations That C++ Can't Do](https://robert.ocallahan.org/2017/04/rust-optimizations-that-c-cant-do_5.html)
- [slice::revswap](https://users.rust-lang.org/t/possible-rust-specific-optimizations/79895/5)

# Comparison to C++ restrict

Some people say that C++ `restrict` is equivalent and widely used but truth is that
> the high amount (?) of bugs regarding that functionality in LLVM expsoed by the Rust compilar
> is an indicator that it's not being widely used there, though
(from [Reddit](https://www.reddit.com/r/rust/comments/px72r1/comment/hem3qy8/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button), [HN](https://news.ycombinator.com/item?id=20944403#20949290) and [HN](https://news.ycombinator.com/item?id=20948546)).

TODO: check usage of restrict in Linux kernel

# Links

Good summary from [HN](https://news.ycombinator.com/item?id=14042318):
  - "Alias analysis has been the holy grail of compiler development for a while. In C++ it's a global, imperfect, and expensive analysis. In Rust you get it for free."

Relevant code is mentioned in [PR #82834](https://github.com/rust-lang/rust/pull/82834).
