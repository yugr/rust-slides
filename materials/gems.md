This is a collection of very important perf-related materials
which all team members need to be aware of.

- [What makes Rust faster than C/C++?](https://www.reddit.com/r/rust/comments/px72r1/what_makes_rust_faster_than_cc/)
  * A lot of high quality comments (a must-read for us):
- [Why ISN'T Rust faster than C?](https://www.reddit.com/r/rust/comments/1at3r6d/why_isnt_rust_faster_than_c_given_it_can_leverage/)
- [Interesting discussion](https://www.reddit.com/r/rust/comments/ab7hsi/comment/ed0u11h/) of how well integer checks can be optimized
- [Myths and Legends about Integer Overflow in Rust](https://huonw.github.io/blog/2016/04/myths-and-legends-about-integer-overflow-in-rust/)
  * Oft-cited article about status of integer overflows in Rust
  * Based on [RFC 560](https://github.com/rust-lang/rfcs/blob/master/text/0560-integer-overflow.md)
- [How to avoid bounds checks in Rust without unsafe](https://shnatsel.medium.com/how-to-avoid-bounds-checks-in-rust-without-unsafe-f65e618b4c1e)
  * Oft-cited article on bounds checks and how to avoid them
- [Back-end parallelism in the Rust compiler](https://nnethercote.github.io/2023/07/11/back-end-parallelism-in-the-rust-compiler.html)
  * How CGUs work
- [Understanding Rusts Auto-Vectorization and Methods for speed](https://users.rust-lang.org/t/understanding-rusts-auto-vectorization-and-methods-for-speed-increase/84891)
- [Memory-safe PNG decoders now vastly outperform C PNG libraries](https://www.reddit.com/r/rust/comments/1ha7uyi/memorysafe_png_decoders_now_vastly_outperform_c/)
  * Good overview of autovec situation
- [What languages (other than Rust) have "zero cost abstraction"?](https://www.reddit.com/r/rust/comments/zkr3xm/what_languages_other_than_rust_have_zero_cost/)
  * Good discussion of what 0-cost means in different languages
- [Rust Performance Book](https://nnethercote.github.io/perf-book)
- [Exploiting Undefined Behavior in C/C++ Programs: The Performance Impact](https://web.ist.utl.pt/nuno.lopes/pubs/ub-pldi25.pdf) (check Wayback Machine if files does not download)
  * Analyzes performance impact of different UB types in C++
  * Very relevant for us
- [RFC: C++ Buffer Hardening](https://discourse.llvm.org/t/rfc-c-buffer-hardening/65734)
  * Adds Rust-like safety checks to STL library
- [Speed of Rust vs C](https://kornel.ski/rust-c-speed)
- [zlib-rs is faster than C](https://trifectatech.org/blog/zlib-rs-is-faster-than-c/)
- [Uninit Read/Write](https://blog.yoshuawuyts.com/uninit-read-write/)
- [Bringing Stack Clash Protection to Clang / X86](https://blog.llvm.org/posts/2021-01-05-stack-clash-protection/)
- [Imprecise floating point operations](https://github.com/rust-lang/rust/issues/21690)
- [Rust loves LLVM](https://llvm.org/devmtg/2024-10/slides/keynote/Popov-Rust_Heart_LLVM.pdf)
  * [Video](https://www.youtube.com/watch?v=Kqz-umsAnk8)
