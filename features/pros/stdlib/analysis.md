# Administrivia

Assignee: yugr

Parent task: gh-38

Effort: 0.5h

# Background

Some of algorithms and containers in Rust are more modern (and consequently faster)
than in C++.

Below we will cover the most known cases.

## Sorting

TODO:
  - algo differences
  - safety overheads in Rust

## Hashtable

TODO:
  - algo differences

## Search tree

TODO:
  - algo differences

# Optimizations

Algorithmic differences are too high-level for compiler to compensate for.

# Workarounds

C++ developers can use alternative implmentations from other libraries
(e.g. Abseil).

# Suggested reading

[Safety vs Performance. A case study of C, C++ and Rust sort implementations](https://github.com/Voultapher/sort-research-rs/blob/main/writeup/sort_safety/text.md)

# Performance impact

## Sort

Results for C++ obtained by running `sort/run.sh` script on
```
$ cat /proc/version
Linux version 6.1.0-26-amd64 (debian-kernel@lists.debian.org) (gcc-12 (Debian 12.2.0-14) 12.2.0, GNU ld (GNU Binutils for Debian) 2.40) #1 SMP PREEMPT_DYNAMIC Debian 6.1.112-1 (2024-09-30)

$ lscpu
...
Vendor ID:                GenuineIntel
  Model name:             Intel(R) Xeon(R) CPU E5-2620 v3 @ 2.40GHz
    CPU family:           6
    Model:                63
...
```

GCC 12:
```
GCC (libstdc++)
Elapsed: 13.0126 s (3677984987 calls)
Elapsed: 13.0075 s (3677984987 calls)
Elapsed: 13.0178 s (3677984987 calls)
Elapsed: 12.9945 s (3677984987 calls)
Elapsed: 13.016 s (3677984987 calls)
```

Clang 20 (libc++):
```
Elapsed: 10.1793 s (2072773777 calls)
Elapsed: 10.2212 s (2072773777 calls)
Elapsed: 10.1872 s (2072773777 calls)
Elapsed: 10.2179 s (2072773777 calls)
Elapsed: 10.1861 s (2072773777 calls)
```

Rust (baseline):
```
$ cargo +baseline b --release
$ target/release/project
Elapsed: 3.630718726s (1942774482 calls)
$ target/release/project
Elapsed: 3.631007281s (1942774482 calls)
$ taget/release/project
Elapsed: 3.65074905s (1942774482 calls)
```

Results must be taken with grain of salt
as there are many different scenarios for sort
(e.g. when array is nearly sorted)
but still Rust is 65% faster than STL.

Comparison counts are very close
so likely they do not influence results much.

## Hashtable

TODO:
  - minibenchmark results

## Search tree

TODO:
  - minibenchmark results

### Runtime improvements

TODO:
  - collect perf measurements for benchmarks:
    * runtime
      + large unexpected changes need to be investigated
    * code size (if applicable)
