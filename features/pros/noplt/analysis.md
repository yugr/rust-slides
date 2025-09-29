# Administrivia

Assignee: yugr

Parent task: gh-49

Effort: 5h

# Background

In Linux shared libraries function calls are done through intermediate
function stubs called PLT stubs which allow runtime linker to delay
symbol resolution and binding until first function call
(see [Dynamic libraries and how to optimize them](https://github.com/yugr/CppRussia/blob/master/2024/EN.pdf)
for more details). This significantly speeds up program startup.

Here is an example for Clang:
```
yugr@cfarm13:~/tasks/rust/noplt/simple-rlib$ LD_DEBUG=statistics clang --help > /dev/null
    798569:
    798569:     runtime linker statistics:
    798569:       total startup time in dynamic loader: 3998818 cycles
    798569:                 time needed for relocation: 3823012 cycles (95.6%)
    798569:                      number of relocations: 22503
    798569:           number of relocations from cache: 50951
    798569:             number of relative relocations: 377144
    798569:                time needed to load objects: 149667 cycles (3.7%)
    798569:
    798569:     runtime linker statistics:
    798569:                final number of relocations: 23149
    798569:     final number of relocations from cache: 50951
yugr@cfarm13:~/tasks/rust/noplt/simple-rlib$ LD_DEBUG=statistics LD_BIND_NOW=1 clang --help > /dev/null
    801121:
    801121:     runtime linker statistics:
    801121:       total startup time in dynamic loader: 10876935 cycles
    801121:                 time needed for relocation: 10615613 cycles (97.5%)
    801121:                      number of relocations: 64979
    801121:           number of relocations from cache: 50951
    801121:             number of relative relocations: 377144
    801121:                time needed to load objects: 225364 cycles (2.0%)
    801121:
    801121:     runtime linker statistics:
    801121:                final number of relocations: 64979
    801121:     final number of relocations from cache: 50951
```
As we can see startup is ~3x slower with full reloc.

On the other hand PLT stubs pollute I$ and BTB and introduce
spurious jump and GOT load for each library call so
for long-running system applications they are harmful.

In 2015 Alex Monakov [proposed](https://gcc.gnu.org/legacy-ml/gcc-patches/2015-05/msg00225.html)
a different approach which trades startup time with runtime
by avoiding PLT stubs completely.
It was reported to bring up to 5-10% performance improvement in practice !

Moreover, if program already enables Full RELRO protection,
it already resolves all symbols at startup (to make GOT read-only)
so disabling PLT should not cost anything.

So Rust uses this approach by default for X86 but not other (RISC) platforms.

Unfortunately this introduces a significant regression...
Basically linkers can optimize PLT calls to direct calls via relaxation.
They can also optimize GOT calls to direct calls but only when
compiler emitted a GOTPCRELX relocation which Rust does not by default
due to some incompatibility issues
(see [#141720](https://github.com/rust-lang/rust/issues/141720) for gory details).

Here is an example of this issue:
```
$ cat repro.rs
extern "C" { fn foo(); }

#[no_mangle]
pub fn bar() {
    unsafe { foo(); }
}

$ rustc +baseline repro.rs --crate-type=rlib -O --emit=asm
bar:
  .cfi_startproc
  jmpq *foo@GOTPCREL(%rip)  // NON-RELOCATABLE RELOCATION

$ cat main.c
void foo() {}
extern void bar();
int main() {
  bar();
  return 0;
}

$ rustc +baseline repro.rs --crate-type=rlib -O --emit=obj
$ gcc main.c repro.o
$ objdump -rd a.out
0000000000001180 <bar>:
    // LINKER FAILED TO OPTIMIZE CALL
    1180:      ff 25 62 2e 00 00      jmpq   *0x2e62(%rip)        # 3fe8 <.got+0x18>
```
If we force proper relocation, linker optimizes well
```
$ rustc +baseline repro.rs --crate-type=rlib -O --emit=asm
$ gcc -c repro.s
$ objdump -rd repro1.o
...
0000000000000000 <bar>:
   0:   ff 25 00 00 00 00       jmpq   *0x0(%rip)        # 6 <bar+0x6>
                        2: R_X86_64_GOTPCRELX   foo-0x4
$ gcc main.c repro.o
$ objdump -rd a.out
0000000000001180 <bar>:
    // LINKER SUCCESSFULLY OPTIMIZED CALL
    1180:      e9 a0 ff ff ff         jmpq   1125 <foo>
```

Note that this is a huge problem because GOT calls are
used in generated assembly even if functions later turn out
to be local (majority of functions do because most Rust programs are linked statically)

Using `-Z default-visibility=protected` (or `hidden`) as suggested
in many places does not help.

TODO:
    * situation in other langs:
      + situation in C/C++
        - e.g. [The New C Standard: An Economic and Cultural Commentary](https://www.coding-guidelines.com/cbook/cbook1_1.pdf)
        - e.g. [Rationale for International Standard Programming Languages - C](https://www.open-std.org/jtc1/sc22/wg14/www/C99RationaleV5.10.pdf)
      + [Java](https://docs.oracle.com/javase/specs/jls/se24/html/),
      + [C#](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/language-specification/introduction)
      + [Go](https://go.dev/ref/spec)
      + [Swift](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/aboutthelanguagereference/)
      + [Fortran](https://j3-fortran.org/doc/year/24/24-007.pdf)
      + Ada ([RM](http://www.ada-auth.org/standards/22rm/html/RM-TOC.html) and [ARM](http://www.ada-auth.org/standards/22aarm/html/AA-TOC.html))
      + [Julia](https://docs.julialang.org)
  - (need to collect prooflinks with timecodes, reprocases for everything)

# Example

TODO:
  - example opt which are caught by this check
  - clear example (Rust microbenchmark, asm code)

# Optimizations

TODO:
  - info whether toolchain can potentially optimize it (and with what limitations)

# Workarounds

Issue with relocs can be worked around via `-Z relax-elf-relocations=yes`
or just by resorting to PLT via `-Z plt=yes`.

One more indirect way is to enable PLT is to disable Full RELRO
(`-C relro-level=partial`).

# Suggested readings

TODO:
  - links to important articles (design, etc.)

# Performance impact

## Prevalence

TODO:
  - is this check is a common case in practice ?
    * may need to write analysis passes to scan real Rust code (libs, big projects) for occurences

## Disabling the check

Because of issue with relocations we want to compare two variants:
  - (A) forced PLT ([yugr/plt/1](https://github.com/yugr/rust-private/tree/yugr/plt/1))
  - (B) GOT + forced relocs ([yugr/noplt-relax/1](https://github.com/yugr/rust-private/tree/yugr/noplt-relax/1))

## Measurements

TODO:
  * collect perf measurements for benchmarks:
    + runtime
    + code size (if applicable)
    + compiler stats
      - depend on feature
      - e.g. SLP/loop autovec for bounds checking feature
      - e.g. NoAlias returns from AA manager for alias feature
      - e.g. CSE/GVN/LICM for alias feature


