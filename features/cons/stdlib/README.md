All info about performance quirks of Rust standard library.

Rust's UTF-8 `String`s have invariant checks which make code slower (compared to `std::string` or `string.h`).

IO is not buffered by default in Rust.

# TODO

- Benchmark disabling of invariant checks in `String`.
