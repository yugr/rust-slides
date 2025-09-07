# Administrivia

Assignee: yugr
Parent task: gh-35
Effort: 1h

TODO:
  - fix all TODOs that are mentioned in feature's README

# Background

Uninitialized variables may cause various types of vulnerabilities.
Firstly attacker may control their initial value and force OOM access
(this is already handled by Rust's bounds checks).
But more importantly they can lead to sensitive information leaks:
```
void foo() {
  char password[32];
  ...
}

void bar() {
  char message[1024];
  if (cond) strcpy(message, “...”);
  // Leaking password if !cond
  printf(message);
}

void baz() {
  foo();
  bar();
}
```

To avoid this Rust forces programmer to initialize all variables.

This feature has been available in commercial toolchains for a long time.
It was [added](https://github.com/microsoft/MSRC-Security-Research/blob/master/presentations/2019_09_CppCon/CppCon2019%20-%20Killing%20Uninitialized%20Memory.pdf)
to Visual Studio in 2019 and to GCC in 2021
(firstly [discussed](https://gcc.gnu.org/legacy-ml/gcc-patches/2014-06/msg00615.html) in 2014).

Microsoft claims that it's been reason for 10% of CVEs in their prodocts (see link above)
Also [Android: Art of Defense](https://www.blackhat.com/docs/us-16/materials/us-16-Kralevich-The-Art-Of-Defense-How-Vulnerabilities-Help-Shape-Security-Features-And-Mitigations-In-Android.pdf)
says that 12% of exploitable bugs in Android are due to uninitialize data.
It's not in [top-25 Mitre vulns](https://cwe.mitre.org/top25/archive/2024/2024_cwe_top25.html)
though and also manual analysis failed to find much:
  - ~50 uninitialized variable CVE in 2024 (1% of buffer overflow CVE)
  - no KEVs in 2024

For this reason C++26 will now silently initialize variables by default
(treating them as Erroneous Behavior).
Note: this feature breaks dynamic checkers like Msan and Valgrind.

Rust uses a more sane approach - instead of selecting default value for all uninit variables
it requires programmer to initialize all automatic variables (scalars, arrays, structs),
refusing to compile code otherwise.

TODO:
  - situation in C/C++
    * e.g. [The New C Standard: An Economic and Cultural Commentary](https://www.coding-guidelines.com/cbook/cbook1_1.pdf)
    * e.g. [Rationale for International Standard Programming Languages - C](https://www.open-std.org/jtc1/sc22/wg14/www/C99RationaleV5.10.pdf)
  - what about heap/globals ?

# Example

TODO:
  - clear example (Rust microbenchmark, asm code)
  - types of check (e.g. compiler/stdlib parts)

# Optimizations

TODO:
  - info whether LLVM can potentially optimize it (and with what limitations)

# Workarounds

TODO:
  - info on how developer can work around it and with how much effort/ugliness (unsafe, wrapping operations, reslicing, etc.)
    * pay special attention to cases which can not be optimized at all

# Suggested readings

TODO:
  - links to important articles (design, etc.)
  - (need to collect prooflinks with timecodes, reprocases for everything)

# Performance impact

Forced initialization overhead for C/C++:
  * [1% in Firefox](https://serge-sans-paille.github.io/pythran-stories/trivial-auto-var-init-experiments.html)
  * may take over 10% on hot paths:
    + [virtio](https://patchwork-proxy.ozlabs.org/project/qemu-devel/patch/20250604191843.399309-1-stefanha@redhat.com/)
    + [Chrome](https://issues.chromium.org/issues/40633061#comment142) (исправление заняло ~4 месяца)
  * [1-3% в среднем на Postgres (до 20% на некоторых кейсах)](https://bugs.launchpad.net/ubuntu/+source/dpkg/+bug/1972043/comments/11)
  * [<1% в Windows](https://github.com/microsoft/MSRC-Security-Research/blob/master/presentations/2019_09_CppCon/CppCon2019%20-%20Killing%20Uninitialized%20Memory.pdf)
  * 4.5% overhead in Clang (https://github.com/yugr/slides/blob/main/CppZeroCost/2025/plan.md)
  * main issue is large local array in hot path (e.g. used for IO) e.g.
    ```
    while (std::getline(maps, line)) {
      char modulePath[PATH_MAX + 1] = "";
      // -ftrivial-auto-var-init вставит здесь memset...
      ret = sscanf(line.c_str(),
                   "%lx-%lx %6s %lx %*s %*x %" PATH_MAX_STRING(PATH_MAX)
                   "s\n",
                   &start, &end, perm, &offset, modulePath);
    }
    ```

## Prevalence

Forced initialization status for C/C++:
  - not enabled by default in Linux distros
    * [Ubuntu discussion](https://bugs.launchpad.net/ubuntu/+source/dpkg/+bug/1972043)
  - [enabled in Chrome](https://issues.chromium.org/issues/40633061)
    * fixing hot paths took ~4 months
  - [not enabled in Firefox](https://serge-sans-paille.github.io/pythran-stories/trivial-auto-var-init-experiments.html)
  - [enabled in Android user/kernel space](https://android-developers.googleblog.com/2020/06/system-hardening-in-android-11.html)

TODO:
  - is this check is a common case in practice ?
    * may need to write analysis passes to scan real Rust code (libs, big projects) for occurences

## Disabling the check

TODO:
  - determine how to enable/disable feature in compiler/stdlib
    * there may be flags (e.g. for interger overflows) but sometimes may need patch code (e.g. for bounds checks)
      + patch for each feature needs to be implemented in separate branch (in private compiler repo)
      + compiler modifications need to be kept in private compiler repo `yugr/rust-private`
    * make sure that found solution works on real examples
    * note that simply using `RUSTFLAGS` isn't great because they override project settings in `Cargo.toml`

## Measurements

TODO:
  * collect perf measurements for benchmarks:
    + runtime
    + PMU counters (inst count, I$/D$/branch misses)
      - actually we failed to understand how to collect PMUs in benchmarks (gh-25)...
    + compiler stats
      - depend on feature
      - e.g. SLP/loop autovec for bounds checking feature
      - e.g. NoAlias returns from AA manager for alias feature
      - e.g. CSE/GVN/LICM for alias feature
  * at least x86/AArch64
    + maybe also normal/ThinLTO/FatLTO, cgu=default/1 in future if we have time
