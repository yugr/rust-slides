All info about performance quirks of Rust standard library.

Rust's UTF-8 `String`s have invariant checks which make code slower (compared to `std::string` or `string.h`).

IO is not buffered by default in Rust so wrap files into `BufWriter` / `BufReader`.

`io::stdout` is line-buffered [both for TTY and for non-TTY streams](https://github.com/rust-lang/rust/issues/60673)
(it's [wrapped in LineWriter](https://users.rust-lang.org/t/why-is-this-rust-loop-3x-slower-when-writing-to-disk/30489/3)).
This makes writes to files very ([10x](https://users.rust-lang.org/t/why-is-this-rust-loop-3x-slower-when-writing-to-disk/30489/7))
slow compared to other languages e.g. Python/Glibc (which line-buffers only TTYS and block-buffers non-TTYs).

Each `print!`/`println!` macro locks output stream. To control locking use
```
let mut lock = io::stdout().lock();
writeln!(lock, "{}", header);
```
Perf book goes into [more details](https://nnethercote.github.io/perf-book/io.html)
on this and stdlib docs [recommend](https://doc.rust-lang.org/stable/std/io/fn.stdout.html)
explicit locking.

Rust default PRNG is of higher quality but slower.

Compiler fails to optimize some stdlib operator adapter combinations (https://github.com/rust-lang/rust/issues/80416)

# TODO

- Benchmark disabling of invariant checks in `String`.
