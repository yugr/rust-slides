All info about performance quirks of Rust standard library.

Rust's UTF-8 `String`s have invariant checks which make code slower (compared to `std::string` or `string.h`).

IO is not buffered by default in Rust.

Compiler fails to optimize some stdlib operator adapter combinations (https://github.com/rust-lang/rust/issues/80416)

# TODO

- Benchmark disabling of invariant checks in `String`.
