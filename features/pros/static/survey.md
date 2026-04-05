Rust functions (and types) are `static` by default
(need to use `pub` to make them public).

This allows compiler to optimize them [more aggressively](https://web.archive.org/web/20240309202636/https://embeddedgurus.com/stack-overflow/2008/12/efficient-c-tips-5-make-local-functions-static/),
like `static` functions in C/C++:
  - more aggressive inlining
  - ABI-violating optimizations (e.g. [IPRA](https://reviews.llvm.org/D23980))
  - change calling convention (to `coldcc` or `fastcc`, see `Transforms/IPO/GlobalOpt.cpp`)
