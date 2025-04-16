This is about missing `-ffast-math` in Rust.

# Solution

- Use `std::intrinsics::XXX_fast` APIs
  * A big disadvantage is that they support only finite numbers (UB otherwise !)
- Use `std::intrinsics::XXX_algebraic` APIs
  * Support non-finite numbers (NaNs and Infs)
