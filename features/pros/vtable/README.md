Virtual functions in Rust (trait objects) are faster than in C++
due to single indirection (vtable is passed as part of fat pointer).

Moreover same Rust object can be passed both as ordinary compile-time trait
(with no runtime overhead) and as dyn trait
(C++ polymorphic objects always have to pay the price of indirect call).

Another benefit is due to the fact that there is no inheritance in Rust
and thus methods of traits can't be overloaded. This allows to make
calls to other methods in method direct (rather than virtual).

On the other hand virtual calls are devirtualized much less aggressively
e.g. in this code
```
pub trait Foo {
    fn foo(&self);
}

pub struct S {}

impl Foo for S {
    fn foo(&self) {}
}

#[no_mangle]
fn glob(x: &dyn Foo) {
    x.foo();
}
```
there is no devirt for `S` in `glob`.

Vtables do not play well with CGUs: they are [duplicated in each CGU](https://github.com/rust-lang/rust/issues/46139).

TODO:
  - watch
Rust vs C++ dynamic dispatch
