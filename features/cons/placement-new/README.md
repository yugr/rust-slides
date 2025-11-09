Rust does not have a placement-new operator like C++.

This is a particular pain when keeping large structs in containers (`Box`, `Vec`,
[BTreeMap](https://github.com/rust-lang/rust/issues/81444), etc.).
For example something like
```
pub fn with_new() -> Box<LargeStruct> {
    Box::new(LargeStruct { ... })
}
```
would first create large struct on stack (potentiall crashing the app)
and then `memcpy` it to heap buffer (may need more complicated example
depending on compiler version).

This effectively means that one
> cannot create a struct that is bigger than the stack allows and
> it will always be created on the stack first and then copied to the heap
(from [here](https://users.rust-lang.org/t/how-to-create-large-objects-directly-in-heap/26405/2)).

The issue is more important in C++ because there copy ctors are potentially more expensive
(not just simple `memcpy`'s).

There have been some RFCs about adding support for placement new
(e.g. [this](https://y86-dev.github.io/blog/return-value-optimization/placement-by-return.html)
or [this](https://github.com/rust-lang/rust/issues/27779))
but according to [this](https://www.reddit.com/r/rust/comments/1eeuqtc/c_vectoremplace_back_vs_rust_vecpushf_copying_v/)
there is nothing officially accepted.
Maintainers consider it [a low priority feature](https://www.reddit.com/r/rust/comments/1eeuqtc/comment/lfhqob6/).

Current effort to implement C++-like guaranteed (unnamed) RVO is in [RFC 2884](https://github.com/rust-lang/rfcs/pull/2884).

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

Also for `Box` this can be solved via `into_boxed_slice`:
```
let boxed_slice: Box<[u8]> = vec![0; 100_000_000].into_boxed_slice();
let boxed_array: Box<[u8; 100_000_000]> = vec![0; 100_000_000].into_boxed_slice().try_into().unwrap();
```

Another common [suggestion](https://www.reddit.com/r/rust/comments/1eeuqtc/comment/lfh557e/)
is to extend the `new` method of container to accept closure
which creates object:
```
container.push_with(|| TheType {a: 1, b: 1})
```
This increases the chance that compiler will be able to elide
the `memcpy` (but still not guarantee it).

Finally some containers provide unsafe APIs for direct allocation and init e.g.
  - `Box` has `alloc` and `init`
  - also `Box` [has](https://github.com/rust-lang/rust/issues/53827#issuecomment-570822294)
```
let a = unsafe {
        let mut a = Box::<[[i32; 2048]; 2048]>::new_uninit();
        ptr::write_bytes(a.as_mut_ptr(), 0, 1);
        a.assume_init()
};
```
  - `Vec` has `with_capacity` and `set_len`
  - `BTreeMap` unfortunately has nothing ?

# Examples

- [#49733](https://github.com/rust-lang/rust/issues/49733#issuecomment-621666613)
- [#53827](https://github.com/rust-lang/rust/issues/53827)
- [How to boxed struct with large size without stack-overflow?](https://users.rust-lang.org/t/how-to-boxed-struct-with-large-size-without-stack-overflow/94961/1)
