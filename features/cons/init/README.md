Rust requires that all variables are initialized at definition.

This may be unnecessary if e.g. buffer will be overwritten later
but compiler will still require dummy initialization.
In some cases it can be optimized later,
in some this will be unnecessary overhead. A typical case is
```
let mut arr : [i32; 5];  // Won't compile
initialize(&arr);
```
Also memory is usually allocated as zero-initialized
(e.g. for `Vec`).

This is similar to GCC's `-ftrivial-auto-var-init` which will become part of C++26
(errouneous behavior, uninitialized vars can be explicitly marked by `[[indeterminate]]`).
Overheads are (based on https://github.com/yugr/slides/blob/main/CppZeroCost/2025/plan.md)
  - 4.5% overhead for Clang X86Builtins.ii compilation
  - 1% Firefox (https://serge-sans-paille.github.io/pythran-stories/trivial-auto-var-init-experiments.html)
  - 10% other (https://patchwork-proxy.ozlabs.org/project/qemu-devel/patch/20250604191843.399309-1-stefanha@redhat.com/ , https://issues.chromium.org/issues/40633061#comment142)
  - 1-20% Postgres (https://bugs.launchpad.net/ubuntu/+source/dpkg/+bug/1972043/comments/11)
  - 1% Windows (https://github.com/microsoft/MSRC-Security-Research/blob/master/presentations/2019_09_CppCon/CppCon2019%20-%20Killing%20Uninitialized%20Memory.pdf)

Another solution for C/C++ is SafeInit:
[paper](https://www.ndss-symposium.org/wp-content/uploads/2017/09/ndss2017_05B-2_Milburn_paper.pdf),
[video](https://www.youtube.com/watch?v=qGzB5x3mnXw)
(I'm not sure how it's related to `-ftrivial-auto-var-init`).

Unfortunately APIs to avoid redundant inits are complex.

One of the most common examples where this hurts is reading files.
Performance overhead may be non-trivial:
  - [7% in stdlib file read](https://github.com/rust-lang/rust/pull/26950)
  - [20-30% in Hyper HTTP library](https://github.com/tokio-rs/tokio/pull/1744#issuecomment-554543881)
  - [30% in shadow simulator](https://github.com/shadow/shadow/issues/1643)
  - [25% for TCP stream](https://github.com/rust-lang/rfcs/pull/837#issuecomment-75497481)
(from [here](https://github.com/rust-lang/rfcs/blob/master/text/2930-read-buf.md#why-not-just-initialize)).

Here's another example for video decoder:
  - [Making the rav1d Video Decoder 1% Faster](https://ohadravid.github.io/posts/2025-05-rav1d-faster/)
  - [Optimizing rav1d, an AV1 Decoder in Rust](https://www.memorysafety.org/blog/rav1d-performance-optimization/)

# Solutions

Note that it's UB to access data before it's initialized (e.g. call `Vec::set_len` on it).
Also it is not valid to construct (shared or mutable) reference to uninitialized memory:
> Creating a reference with &/&mut is only allowed if the pointer
> is properly aligned and points to initialized data. 
(from [here](https://doc.rust-lang.org/std/ptr/macro.addr_of_mut.html),
also see [this](https://github.com/rust-lang/rfcs/blob/master/text/2930-read-buf.md#but-how-bad-are-undefined-values-really)
for example of real UB). Only pointers should be used to avoid UB.

The suggested solution for simple types is `MaybeUninit`.
There once was `std::mem::uninitialized()` but it's no longer recommended.

E.g. for arrays:
```
let buf = unsafe {
    let mut buf = MaybeUninit::<[u8; 4]>::uninit();
    let ptr = buf.as_mut_ptr();
    for i in ... {
        ptr.offset(i).write(...);
    }
    buf.assume_init()
};
```
and for structs:
```
let role = unsafe {
    let mut uninit = MaybeUninit::<Role>::uninit();
    let ptr = uninit.as_mut_ptr();
    // Need write (instead of explicit assign) to avoid dropping uninitialized String
    addr_of_mut!((*ptr).name).write("basic".to_string());
    (*ptr).flag = 1;
    (*ptr).disabled = false;
    uninit.assume_init()
};
```
(see more examples [here](https://blog.logrocket.com/unsafe-rust-how-and-when-not-to-use-it/#dealingwithuninitializedmemory)).

For vectors we have dedicated `spare_capacity_mut` API :
```
let mut buf: Vec<u8> = ...;

let old_len = buf.len();
buf.reserve(data.len());

unsafe {
    let ptr = buf.spare_capacity_mut();
    for i in ... {
        ptr[idx].write(...);
    }
    buf.set_len(len + data.len());
}
```

For reading from files into uninitialized buffers we can use `Read::read_buf` APIs:
```
let mut buf = [MaybeUninit::uninit(); 4096];
let mut buf = BorrowedBuf::from(&mut buf[..]);
rd.read_buf(buf.unfilled())?;
if buf.len() == 0 {
    break Ok(());
}
// Work with buf.filled()
```
(new API proposals [keep coming up](https://blog.sunfishcode.online/writingintouninitializedbuffersinrust/)).

Another common case is `char::encode_utf8(&mut [u8]) -> &mut str`.
It requires _initialized_ slice as input and LLVM is not clever enough
to realize that initialization is redundant (because UTF-8 is variable-length).
