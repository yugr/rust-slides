All info about large Rust binaries.

Rust binaries are known to be significantly larger than C.
This is true for small programs (i.e. embedded use-cases) but becomes even more astonishing for the larger ones
(hundreds of MBs are not uncommon, see [upstream #66348](https://github.com/rust-lang/rust/issues/66348)).

Helloworld sizes on Windows:
```
-rwxr-xr-x 1 Asus None 8.5K Mar 14 22:36 c.exe
-rwxr-xr-x 1 Asus None 9.0K Mar 14 22:37 cc.exe
-rwxr-xr-x 1 Asus None 121K Mar 14 22:37 opt.exe
-rwxr-xr-x 1 Asus None 137K Mar 14 22:37 unopt.exe
```

This area is studied very well: see [min-sized-rust](https://github.com/johnthagen/min-sized-rust)
for complete guide.

There are several reasons for this:
  - release binaries are not stripped by default (for `RUST_BACKTRACE`)
    * can be worked around in Cargo.toml or just running `strip` on binary
  - remove parts of stdlib:
    * stack unwinding code and symbolizer
      + can be disabled via `panic=abort` in Cargo.toml
    * other parts of stdlib (e.g. formatting)
    * jemalloc [no longer a problem](https://github.com/johnthagen/min-sized-rust/blob/main/README.md#remove-jemalloc)
  - code dup due to monomorphization (see analysis [here](https://nickb.dev/blog/the-dark-side-of-inlining-and-monomorphization/))
    * can be fixed by not-template-base hack from C++: [What’s the name of this technique for cutting down compile times from monomorphization?](https://users.rust-lang.org/t/whats-the-name-of-this-technique-for-cutting-down-compile-times-from-monomorphization/89172)
  - shared libraries are not widely used (if at all)
    * unfixable until stable ABI and binary package distributions are introduced
    * `cargo bloat` can be used to identify the most problematic dependencies
    * need to watch out for different versions of same library (see example [here](https://oknozor.github.io/blog/optimize-rust-binary-size/))

LTO and opt-level Z may also help (see [here](https://rustwasm.github.io/docs/book/reference/code-size.html)).

More low-level magic can be done (see e.g. [Windows hacks](https://github.com/mcountryman/min-sized-rust-windows))
but probly 99% of users will not use them anyway.

# TODO

- Make size comparison on Linux
