# Administrivia

Assignee: yugr
Parent task: gh-35
Effort: 16h

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
  - [1% in Firefox](https://serge-sans-paille.github.io/pythran-stories/trivial-auto-var-init-experiments.html)
  - may take over 10% on hot paths:
    * [virtio](https://patchwork-proxy.ozlabs.org/project/qemu-devel/patch/20250604191843.399309-1-stefanha@redhat.com/)
    * [Chrome](https://issues.chromium.org/issues/40633061#comment142) (fixing hot paths took ~4 months)
  - [1-3% on average in Postgres (up to 20% in some cases)](https://bugs.launchpad.net/ubuntu/+source/dpkg/+bug/1972043/comments/11)
  - [<1% in Windows](https://github.com/microsoft/MSRC-Security-Research/blob/master/presentations/2019_09_CppCon/CppCon2019%20-%20Killing%20Uninitialized%20Memory.pdf)
    * 4% initially
    * solved by
      + apply only to PODs
      + opt-out i.e. disabling on hot paths (only 1 instance in Windows kernel)
      + more precise analysis in compiler
  - 4.5% overhead in Clang (https://github.com/yugr/slides/blob/main/CppZeroCost/2025/plan.md)
  - main issue is large local array in hot path (e.g. used for IO) e.g.
    ```
    while (std::getline(maps, line)) {
      char modulePath[PATH_MAX + 1] = "";
      // -ftrivial-auto-var-init inserts memset here...
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
  - [not enabled in Firefox](https://serge-sans-paille.github.io/pythran-stories/trivial-auto-var-init-experiments.html)
  - [enabled in Android user/kernel space](https://android-developers.googleblog.com/2020/06/system-hardening-in-android-11.html)

To see how often initializations are dead in practice
we created a small Valgrind plugin [DeadWrites](https://github.com/yugr/valgrind/tree/yugr/deadwrites/3)
(this was before I learned about excellent [deadstores plugin](https://kristerw.blogspot.com/2020/02/watching-for-software-inefficiencies.html)
by Krister Walfridsson).
The plugin counts amount of dead (unused) bytes stored to memory
and has a 300-400x slowdown.
Note that not all dead writes come from Rust's initializations
so this is just an approximation.

Results for oxipng:
```
$ cargo clean && valgrind --trace-children=yes --tool=deadwrites cargo +baseline b --release -j 1 |&  tee build.log
$ ./count_dw_stats.py < build.log
9% (42725023150 out of 450234323338)
```

TODO:
  - dead writes stats for Clang

## Disabling the check

It's not really possible to disable this check per language rules...

## Measurements

Rather than measuring Rust, we compare Clang with and without `-ftrivial-auto-var-init`.
In [Hardening: current status and trends](https://github.com/yugr/slides/blob/main/CppZeroCost/2025/EN.pdf)
the authors reported 4.5% degradation for Clang (compilation of CGBuiltins.ii).

TODO:
  - compiler stats
    * count stores (and memsets) inside loops
