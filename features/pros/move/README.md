This is about Rust's move-by-default feature.

Rust has _destructive_ moves i.e. destructor of moved object is not called afterwards.
Examples of this:
  - [example 1](https://www.reddit.com/r/rust/comments/px72r1/comment/hem26o0/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button)
  - [example 2](https://www.reddit.com/r/rust/comments/px72r1/comment/heqmrjh/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button)

Also Rust's move is just a `memcpy` which is a single instruction in LLVM IR
so much easier to optimize in middle-end.

Example of cost of copies in large C++ codebase : https://groups.google.com/a/chromium.org/g/chromium-dev/c/EUqoIz2iFU4/m/kPZ5ZK0K3gEJ
