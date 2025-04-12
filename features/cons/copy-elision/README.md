Rust does not always perform move/copy elision.

Rust copies/moves are side-effect-free (have "no user-visible
effects") so it does not need special copy-elision rules
like C++. So in theory compiler is capable of
removing all redundant `memcpy`'s.
E.g. Rust had (non-guaranteed) (N)RVO since day one.

E.g. C++ code like
```c++
#include <utility>

class A {
public:
  A(A &&);
  A(const A &);
};

void sink(const A &);

void mov(A a) {
  A a1 = std::move(a);
  A a2 = std::move(a1);
  sink(a2);
}

void cpy(A a) {
  A a1(a);
  A a2(a1);
  sink(a2);
}
```
is not optimized by Clang/GCC whereas equivalent Rust code contains just 1 `memcpy` :
```rust
use std::hint::black_box;

#[derive(Clone)]
pub struct A {
  pub data: [i32; 1024],
}

pub fn mov(a: A) {
    let a = a;
    let a = a;
    black_box(&a);
}

pub fn cpy(a: A) {
    let a = a.clone();
    let a = a.clone();
    black_box(&a);
}
```
(compile via `rustc -O --emit asm --crate-type=lib repro.rs -o- | c++filt`).

[copyless](https://github.com/kvark/copyless) trait has been removed
because situation w/ `memcpy`'s has been significantly improved.

In many cases Rust keeps spurious `memcpy`'s esp. on function bondary:
```
use std::hint::black_box;

#[derive(Clone)]
pub struct A {
  pub data: [i32; 1024],
}

pub fn mov(a: A) {
    black_box(a);
}
```

The reason is that LLVM is not always good at optimizing `memcpy`
so Rust has [custom optimization passes](https://github.com/rust-lang/rust/blob/master/compiler/rustc_mir_transform/src/dest_prop.rs) to deal with them.
This work is [ongoing](https://github.com/rust-lang/rust/labels/A-mir-opt-nrvo)
e.g. [#91521](https://github.com/rust-lang/rust/issues/91521) has been fixed
and [#32966](https://github.com/rust-lang/rust/issues/32966)
and [#79914](https://github.com/rust-lang/rust/issues/79914) haven't.
Some info on why this may happen can be found in [#103172](https://github.com/rust-lang/rust/pull/103172).

# Solutions

Pass large structs by reference.

Enable additional MIR opts (does not help with case above though):
  - `-Zmir-enable-passes=+DestinationPropagation,+RenameReturnPlace`
  - `-Zmir-opt-level=4`
  - (may need to prepend `-Zunsound-mir-opts`)

(does not help in all cases).

# Examples

- [#116541](https://github.com/rust-lang/rust/issues/116541)

# TODO

- Read comments about problems with copy elision in `dest_prop.rs` and `nrvo.rs`
- Why Rust generates `memcpy` in simple example above ?
