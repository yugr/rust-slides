Rust's thread-local variables may have some overheads compared to C++ `__thread`.

There are two implementations: `thread_local!` macro and `#[thread_local]` attribute.

Also by default Rust uses `global-dynamic` TLS model
(according to [compiler/rustc_target/src/spec/mod.rs](https://github.com/rust-lang/rust/blob/master/compiler/rustc_target/src/spec/mod.rs)):
> Thread-local storage (TLS) model is very pessimistic by default.
> Makes rayon much slower (tls_get_addr very high in profiles).
(from [here](https://hackmd.io/@Q66MPiW4T7yNTKOCaEb-Lw/gosim-unconf-rust-codegen)).
We can opt-out via `-Z tls-model=local-exec` but
even then we seem to get slightly worse asm than GCC (see TODO below).

# `thread_local!`

This is the recommended solution but it has several drawbacks.

Firstly such variable has to be interiory mutable so `Cell` or `RefCell`.
`Cell` has no overhead but is only applicable to primitive types
(huge overheads otherwise) and `RefCell` introduces runtime checking overhead
(`borrow_mut`, etc.).

Secondly TLS variables with non-trivial init value or destructor
are runtime checked on every access
(for lazy initialization or detecting that variable is no longer valid).

Lazy initialization is likely due to avoid init order fiasco ?

With const init value, no destructor and `local-exec` TLS model
code is as good as C++.

For more details see [TLS implementation](https://github.com/rust-lang/rust/blob/master/library/std/src/thread/local.rs)
(main part in `thread_local/native/mod.rs`).

# `#[thread_local]`

This attribute directly marks global as thread-local in LLVM IR.

TODO

# TODO

- Why `#[thread_local]` is not widely used ?
- Why these [C++](https://godbolt.org/z/7Pc8sWvWo)
```
__thread unsigned x;

unsigned foo() {
  return x++;
}
```
and [Rust](https://godbolt.org/z/W4vP6Mnd4)
```
use std::cell::Cell;
use std::thread;

thread_local!(static FOO: Cell<u32> = const { Cell::new(1) });

pub fn foo() -> u32 {
  let ans = FOO.get();
  FOO.set(ans + 1);
  ans
}
```
  codes do not generate matching asm ? One reason is different default tls model but even with initial-exec for both Rust matches GCC's `-fPIC` (not `-fPIE`).
  This may be due to `-C relocation-model=pic` being default for (even static) libs ?!
