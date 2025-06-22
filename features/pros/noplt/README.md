Rust enables `-fno-plt` by default so instead of using
```
call example::foo@PLT
```
it has
```
call qword ptr [rip + example::foo@GOTPCREL]
```

Avoiding PLT is generally faster:
  - 1 jump per external call instead of 2
  - less I$ and BTB pressure
  - GOT address may be LICM-ed
but incurs more startup overheads
(it disables lazy binding so need to resolve all symbols on start).

See [this question](https://internals.rust-lang.org/t/function-calls-plt-vs-gotpcrel/8909)
for details.

Also note that Rust [uses `-fno-semantic-interposition` by default](https://github.com/rust-lang/rustc_codegen_gcc/issues/53)
(not deliberately but through the virtue of being based on LLVM).
