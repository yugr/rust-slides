# Administrivia

Assignee: yugr

Parent task: gh-38

Effort: 1.5h

# Background

Some of algorithms and containers in Rust are more modern (and consequently faster)
than in C++.

Below we will cover the most known cases.

## Sorting

Stable sort (`sort()`) uses driftsort algorithm and
unstable (`sort_unstable()`) uses ipnsort.
Both were written to facilitate ILP rather than SIMD for simple types
(as in at least libc++ STL - see comments about vectorization in
`libcxx/include/__algorithm/sort.h`).

Rust by default uses stable sort (`std::stable_sort`) and
algo is written in such way that even broken comparators
don't break memory safety (i.e. access invalid indices).

## Hashtable

C++ Standard imposes strict rules on `unordered_map`.
Most notably, references to container elements must remain valid
in presense of insertions so this restricts implementation to
vector of lists. This causes following problems:
  - even if there are no conflicts we have one additional indirection
  - all insertions require malloc ("per-element overhead")
  - poor cache locality

In Rust, this rule is not imposed - moreover it's totally unnecessary
because we can't modify container while holding reference to any element.
So Rust uses open addressing hash tables.

On the other hand Rust's hash function (SipHash) is slower and more secure.

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

SipHash has a very high overhead (5.2 sec.)
compared to (less secure) `ahash` (2.9 sec.)
and `fxhash` (2.5 sec.).

Corresponding C++ program is
  - gcc 12 with libstdc++: 3.6 sec.
  - Clang 20 with libc++: 1 sec.

So it seems C++ performance is now better than Rust.

## Search tree

TODO:
  - minibenchmark results
