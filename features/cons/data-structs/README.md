Rust memory model requires single mutable reference at at any point in time.
This is enforced in simple cases by borrow checker
but in more complex cases require unsafe code or runtime checks.

# Solutions

Non-trivial data structures / reference graphs can be represented through various means.
[This link](https://users.rust-lang.org/t/how-can-we-teach-people-about-self-referential-types/65362)
suggests several options:
  - refactor data struct to have dedicated object for owning referenced entities (e.g. allocator)
    * e.g. Parser does not need to own the buffer
  - use indices
    * e.g. store graph as array of nodes + pred/succ indices
  - use runtime checks (`Rc` (`Arc`), `RefCell`);
    the overheads [are](https://users.rust-lang.org/t/how-expensive-is-rc-refcell-borrow-mut/26713/5):
    * calls to borrow/borrow_mut require a write so an exclusive cache-line access (ok for borrow_mut (it'll likely write anyway) but not for read-only borrow)
    * extra fields may increase D$ pressure
    * note that C++ `shared_ptr` is [cheaper](/home/Asus/src/gcc-03fb8f2/libstdc++-v3/include/bits/shared_ptr.h) than `Arc<RefCell>`
  - (for performance-critical code) raw pointers and unsafe
    * very error prone

# TODO

- Check overhead of `Rc` (`Arc`) / `RefCell` by disabling checks in large projects
