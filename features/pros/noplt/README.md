Rust [enables](https://github.com/rust-lang/rust/pull/109982)
`-fno-plt` by default on X86 so instead of using
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
Take rustc for example:
```
yugr@cfarm13:~/tasks/rust$ LD_DEBUG=statistics gcc -S -O2 hello.c
   ...
   1850804:     runtime linker statistics:
   1850804:       total startup time in dynamic loader: 348254 cycles
   1850804:                 time needed for relocation: 172392 cycles (49.5%)
   1850804:                      number of relocations: 972
   1850804:           number of relocations from cache: 22
   1850804:             number of relative relocations: 1676
   1850804:                time needed to load objects: 141348 cycles (40.5%)
   ...

# Cold start
$ LD_DEBUG=statistics rustc +baseline -O hello.rs
   ...
   1491806:     runtime linker statistics:
   1491806:       total startup time in dynamic loader: 23059019 cycles
   1491806:                 time needed for relocation: 18940150 cycles (82.1%)
   1491806:                      number of relocations: 22152
   1491806:           number of relocations from cache: 5842
   1491806:             number of relative relocations: 574276
   1491806:                time needed to load objects: 4072926 cycles (17.6%)
   ...

# Hot start
$ LD_DEBUG=statistics rustc +baseline -O hello.rs
   ...
   1492625:     runtime linker statistics:
   1492625:       total startup time in dynamic loader: 5199864 cycles
   1492625:                 time needed for relocation: 5041503 cycles (96.9%)
   1492625:                      number of relocations: 22152
   1492625:           number of relocations from cache: 5842
   1492625:             number of relative relocations: 574276
   1492625:                time needed to load objects: 132518 cycles (2.5%)
   ...
```
On the other hand rustc with libs is much much larger than cc1...

See [this question](https://internals.rust-lang.org/t/function-calls-plt-vs-gotpcrel/8909)
for details.

Also note that Rust [uses `-fno-semantic-interposition` by default](https://github.com/rust-lang/rustc_codegen_gcc/issues/53)
(not deliberately but through the virtue of being based on LLVM).
