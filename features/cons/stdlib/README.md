All info about performance quirks of Rust standard library.

Compiler fails to optimize some stdlib operator adapter combinations (https://github.com/rust-lang/rust/issues/80416)

Rust's UTF-8 `String`s have invariant checks which make code slower (compared to `std::string` or `string.h`).

Rust default PRNG is of higher quality but slower.

# Checks

In general Rust's stdlib checks many invariants even in release
e.g. in `library/core/src/slice/mod.rs`:
```
    pub const fn chunks(&self, chunk_size: usize) -> Chunks<'_, T> {
        assert!(chunk_size != 0, "chunk size must be non-zero");
        Chunks::new(self, chunk_size)
    }
```

Also many APIs force you to perform the necessary checks
e.g. forced "NULL checks" (via `Option::unwrap` or `Option::expect`)
for APIs that return `Option`.

# IO

IO is not buffered by default in Rust so wrap files into `BufWriter`/`BufReader` adaptors
(efriedman reports [20x improvement](https://github.com/rust-lang/rust/issues/28073#issue-103786362)).
Some standard streams always come as buffered so check the docs.
`BufReader` will only fetch more data when [internal buffer is exhausted](https://graphallthethings.com/posts/better-buf-read)
which may be suboptimal.
Of course [nothing can beat](https://users.rust-lang.org/t/performance-reading-file-parse-from-io-read-vs-from-u8/91948)
single complete file read (10x reported [here](https://github.com/serde-rs/json/issues/160#issuecomment-253446892)).

`io::stdout()` is line-buffered [both for TTY and for non-TTY streams](https://github.com/rust-lang/rust/issues/60673)
(it's [wrapped in LineWriter](https://users.rust-lang.org/t/why-is-this-rust-loop-3x-slower-when-writing-to-disk/30489/3)).
This makes writes to files very ([10x](https://users.rust-lang.org/t/why-is-this-rust-loop-3x-slower-when-writing-to-disk/30489/7))
slow compared to other languages e.g. Python/Glibc (which line-buffers only TTYS and block-buffers non-TTYs).

`BufRead` trait's most popular method is `lines()` which returns `String`'s.
This has [huge overhead](https://internals.rust-lang.org/t/extend-io-bufread-to-read-multiple-lines-at-once/10196)
due to per-line allocation and UTF-8 verification.
A [better approach](https://users.rust-lang.org/t/why-using-the-read-lines-iterator-is-much-slower-than-using-read-line/92815)
is to use `BufRead::read_line` to read into non-owned buffer.
Interestingly [docs](https://doc.rust-lang.org/nightly/rust-by-example/std_misc/file/read_lines.html)
do not suggest it...

Each `print!`/`println!` macro locks output stream. To control locking use
```
let mut lock = io::stdout().lock();
writeln!(lock, "{}", header);
```
Perf book goes into [more details](https://nnethercote.github.io/perf-book/io.html)
on this and stdlib docs [recommend](https://doc.rust-lang.org/stable/std/io/fn.stdout.html)
explicit locking.

# TODO

- Benchmark disabling of invariant checks in `String`
- Benchmark disable of checks in `Option::unwrap` and `Option::expect`
