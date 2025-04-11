Rust does not have a placement-new operator like C++.

This is a particular pain when keeping large structs in containers (`Box`, `Vec`, etc.).
For example something like
```
pub fn with_new() -> Box<Pages> {
    Box::new(LargeStruct { ... })
}
```
would first create large struct on stack (potentiall crashing the app)
and then `memcpy` it to heap buffer.

This effectively means that one
> cannot create a struct that is bigger than the stack allows and
> it will always be created on the stack first and then copied to the heap
(from [here](https://users.rust-lang.org/t/how-to-create-large-objects-directly-in-heap/26405/2)).

# Solutions

One could argue that lack of placement new may be alleivated
by better copy elision but
  - copy elision is not guaranteed
  - copy elision may depend on compiler version
  - copy elision requires optimizations so will not work in debug

Box recently got a [workaround](https://users.rust-lang.org/t/construct-a-box-i32-32-32-32-without-hitting-stack/71214)
for this.

A poor man's placement new used to be
```
let boxed: Boxed<BigStruct> = box foo();
```
(not sure if it works now).

There have been some RFCs about adding support for placement new
but according to [this](https://www.reddit.com/r/rust/comments/1eeuqtc/c_vectoremplace_back_vs_rust_vecpushf_copying_v/)
there is nothing officially accepted.
Maintainers consider it [a low priority feature](https://www.reddit.com/r/rust/comments/1eeuqtc/comment/lfhqob6/).

# Examples

- [#49733](https://github.com/rust-lang/rust/issues/49733#issuecomment-621666613)
- [How to boxed struct with large size without stack-overflow?](https://users.rust-lang.org/t/how-to-boxed-struct-with-large-size-without-stack-overflow/94961/1)
