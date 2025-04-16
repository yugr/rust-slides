This is about missing `-ffast-math` in Rust.

# Solution

- Use `std::intrinsics::XXX_fast` APIs
  * A big disadvantage is that they support only finite numbers (UB otherwise !)
  * [Wrappers](https://github.com/bluss/fast-floats) also available
- Use `std::intrinsics::XXX_algebraic` APIs
  * Support non-finite numbers (NaNs and Infs)
- Does `-C llvm-args=-ffast-math` work ?
