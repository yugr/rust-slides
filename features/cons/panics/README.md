All info about performance overhead of panics.

Panics involve stack unwinding and destructors so are definitely not free.

Rust has `panic=abort` (similar to C++ `-fno-exceptions`)

# TODO

Does `panic=abort` avoid all overheads ?

Check if these C++-specific overheads apply:
  - "Исключения C++ через призму компиляторных оптимизаций" (https://www.youtube.com/watch?v=ItemByR4PRg)
  - https://devblogs.microsoft.com/oldnewthing/20220228-00/?p=106296
