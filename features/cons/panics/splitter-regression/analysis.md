Failing to remove dead code is due a mix of several factors:
  - lld linker marks all symbols referenced by LSDAs in `.eh_frame` sections
    as live
    * this is a [known feature](https://maskray.me/blog/2021-02-28-linker-garbage-collection)
  - LSDAs (`.gcc_except_table` sections) do not reference any symbols in normal mode
    but LSDA for function with outlined blocks do reference address of outlined function
    * see proof below
  - in some cases outlined blocks may contain references to normal blocks
    (e.g. some code is shared by normal and exceptional flow)
  - this will cause original code to be marked as live

Reported upstream in [issue #165139](https://github.com/llvm/llvm-project/issues/165139).

# Real example

We will illustrate the problem with `_ZN5tokio7process3imp17GlobalOrphanQueue12reap_orphans...`
functions in tokio project.

Original code contains just one of them but splitter-enabled code has two symbols
(the second fails to be GC-ed).

Compiled with reference compiler:
  - `_ZN5tokio7process3imp17GlobalOrphanQueue12reap_orphans17h24a43c4177dae6c9E` (from target/release/deps/tokio-f5dda5b171239ad8.tokio.722335c960bf188b-cgu.0.rcgu.o)
  - `_ZN5tokio7process3imp17GlobalOrphanQueue12reap_orphans17h7b80797cbf02d0faE` (from /home/yugr/tasks/rust/bench/tokio-ref/target/release/deps/libtokio-4ac87b2d2b439df0.rlib, removed via `--gc-sections`)

Compiled with splitter:
  - `_ZN5tokio7process3imp17GlobalOrphanQueue12reap_orphans17hd698893702fb78ffE` and `_ZN5tokio7process3imp17GlobalOrphanQueue12reap_orphans17hd698893702fb78ffE.cold` (from target/release/deps/tokio-f5dda5b171239ad8.tokio.5721d78e79eefb11-cgu.0.rcgu.o)
  - `_ZN5tokio7process3imp17GlobalOrphanQueue12reap_orphans17hfc391815ffd285f1E` and `_ZN5tokio7process3imp17GlobalOrphanQueue12reap_orphans17hfc391815ffd285f1E.cold` (from target/release/deps/libtokio-4ac87b2d2b439df0.rlib, NOT removed via `--gc-sections`)

We can see why _ZN5tokio7process3imp17GlobalOrphanQueue12reap_orphans17hfc391815ffd285f1E wasn't removed by tracing lld (see attached patch):
  * scan eh sections roots
  * `.gcc_except_table._ZN5tokio7runtime7builder7Builder5build17h3367e20f4190c060E`
  * `.text.split._ZN5tokio7runtime7builder7Builder5build17h3367e20f4190c060E`
  * `_ZN5tokio7runtime7builder7Builder5build17h3367e20f4190c060E` (this is the problem, outlined block calls back original function)
  * `.data.rel.ro..Lanon.6393adea5802c703350f780788312f7f.846`
  * `_ZN5tokio7runtime4task3raw4poll17h1069132c40d27ed4E`
  * `_ZN5tokio7runtime9scheduler12multi_thread6worker3run17h6557a39dd942c2bbE`
  * `_ZN5tokio7runtime9scheduler12multi_thread6worker7Context12park_timeout17h66577d32e7a3e917E`
  * `.text._ZN5tokio7runtime6driver6Driver12park_timeout17haecd5973a5be95c5E`
  * `_ZN5tokio7process3imp17GlobalOrphanQueue12reap_orphans17hfc391815ffd285f1E`

Problematic code in `.text.split._ZN5tokio7runtime7builder7Builder5build17h3367e20f4190c060E`:
```
Problem is in XXX:
 7e4:   e9 00 00 00 00          jmpq   7e9 <_ZN5tokio7runtime7builder7Builder5build17h3367e20f4190c060E.cold+0x7e9>
                        7e5: R_X86_64_PLT32     .text._ZN5tokio7runtime7builder7Builder5build17h3367e20f4190c060E+0x16da
```

# LSDAs example

```
$ cat repro.rs
extern "Rust" { fn foo(dummy: &mut Vec<i32>); }

pub fn copy2() -> i32 {
    let mut dummy = Vec::<i32>::new();
    unsafe { foo(&mut dummy); }
    return 123;
}

$ rustc +baseline -O --crate-type=rlib --emit=obj repro.rs
$ objdump -r repro.o
...  # No relocations in .gcc_except_table._ZN6repro25copy217h54b32f5584c02c14E


$ rustc +baseline -O --crate-type=rlib --emit=obj repro.rs -Cllvm-args='-enable-split-machine-functions -mfs-split-ehcode'
$ objdump -r repro.o
...
RELOCATION RECORDS FOR [.gcc_except_table._ZN6repro25copy217h54b32f5584c02c14E]:
OFFSET           TYPE              VALUE
0000000000000001 R_X86_64_PC64     .text.split._ZN6repro25copy217h54b32f5584c02c14E
0000000000000011 R_X86_64_PC64     .text.split._ZN6repro25copy217h54b32f5584c02c14E
...
```
