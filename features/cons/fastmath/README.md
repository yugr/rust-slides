This is about missing `-ffast-math` in Rust.

It's a huge problem particularly [for gamedev](https://github.com/rust-lang/rust/issues/21690#issuecomment-1589427278):
> This particular feature is a real need within the game development community
> for obvious performance reasons. Usually we'd want this for hot-spot optimizations,
> however, it's also common to blanket enable -ffast-math for the entire (C++) game codebase.
but also [other domains](https://github.com/rust-lang/rust/issues/21690#issuecomment-1589427278):
> lack of even opt-in location-specific fast math (such as fadd_fast and fmul_fast)
> on stable hinders the use of Rust in some key algorithms for computer vision,
> robotics and augmented reality applications

Note that Fortran effectively has fast-math (or at least `-fassociative-math`) by default.

Rust developers have [clearly rejected](https://github.com/rust-lang/rust/issues/21690#issuecomment-1589427278)
global fast math flag.

# Solution

- Use `std::intrinsics::XXX_fast` APIs
  * A big disadvantage is that they support only finite numbers (UB otherwise !)
  * [Wrappers](https://github.com/bluss/fast-floats) also available
  * In unstable :(
- Use `std::intrinsics::XXX_algebraic` APIs
  * Support non-finite numbers (NaNs and Infs)
  * In unstable :(
- Use `-C llvm-args=-ffast-math` (does it work ?)
- Request for fast-math has been rejected in [upstream #21690](https://github.com/rust-lang/rust/issues/21690)

# Examples

A lot of issues are linked in [upstream #21690](https://github.com/rust-lang/rust/issues/21690).

# TODO

- Is `-C llvm-args=-ffast-math` enough to enable fast math ? If not - why ?
- Add compile flag to enable fast-math and see how it affects runtime performance and CSE/GVN/LICM/LoopVectorize statistics (esp. autovec)
