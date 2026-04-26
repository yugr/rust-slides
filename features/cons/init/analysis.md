# Administrivia

Assignee: yugr

Parent task: gh-35

Effort: 23h

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

In C/C++ three types of memory (automatic, heap and static storage)
are initialized by different means:
  - automatic: by compiler under special flag (optional before C++26)
  - heap: by hardened allocator (optional)
  - global: by OS or startup code (required by the language:
    "all objects with static storage duration shall be initialized
    (set to their initial values) before program startup")

Initialization of heap and globals has been done
since forever, via opt-in hardened allocators and
forced zero-initialization in kernel (both `brk` and
[anonymous `mmap`'s](https://stackoverflow.com/a/65084762/2170527)
zero-initialize mapped pages).

Automatic variable initialization has higher overhead
and is less explored. It has been available
in commercial C/C++ toolchains for a long time
(e.g. Diag Data Compiler `-Xinit-locals-mask` option).
It has also been a MISRA requirement for a long time.
It was [added](https://github.com/microsoft/MSRC-Security-Research/blob/master/presentations/2019_09_CppCon/CppCon2019%20-%20Killing%20Uninitialized%20Memory.pdf)
to Visual Studio in 2019,
[to Clang](https://lists.llvm.org/pipermail/cfe-dev/2018-November/060304.html) in 2018 and
to GCC in 2021 (firstly [discussed](https://gcc.gnu.org/legacy-ml/gcc-patches/2014-06/msg00615.html) in 2014,
not counting [Fortran `-finit-local-zero` in 2007](https://gcc.gnu.org/legacy-ml/fortran/2007-06/msg00028.html)).

Microsoft claims that it's been reason for 10% of CVEs in their products (see link above)
Also [Android: Art of Defense](https://www.blackhat.com/docs/us-16/materials/us-16-Kralevich-The-Art-Of-Defense-How-Vulnerabilities-Help-Shape-Security-Features-And-Mitigations-In-Android.pdf)
says that 12% of exploitable bugs in Android are due to uninitialize data.
It's not in [top-25 Mitre vulns](https://cwe.mitre.org/top25/archive/2024/2024_cwe_top25.html)
though and also manual analysis failed to find much
(most likely such variables get attributed as buffer overflows or ASLR leaks):
  - ~50 uninitialized variable CVE in 2024 (1% of buffer overflow CVE)
  - no KEVs in 2024

For this reason C++26 will now silently initialize variables by default
(treating them as Erroneous Behavior).
Note: this feature breaks dynamic checkers like Msan and Valgrind.

Rust uses a more sane approach - instead of selecting default value for all uninit variables
it requires programmer to initialize all automatic variables (scalars, arrays, structs),
refusing to compile code otherwise.

[C#](https://stackoverflow.com/questions/30816496/why-do-local-variables-require-initialization-but-fields-do-not).
and [Swift](https://kyouko-taiga.github.io/swift-thoughts/tutorial/chapter-1/)
also require initialization.
Plain Ada allows uninitilized but SPARK extension prohibits it.
Java and [Go](https://go.dev/ref/spec#The_zero_value) initialize variables
with zero default value
(which is arguable a [bad idea](https://lists.llvm.org/pipermail/cfe-dev/2018-November/060321.html)
but [generates better code](https://lists.llvm.org/pipermail/cfe-dev/2018-December/060540.html)).
Interestingly enough, old Fortran codes relied on zero locals
which is the reasons for [`-finit-local-zero` in `gfortran`](https://gcc.gnu.org/legacy-ml/fortran/2007-06/msg00028.html).

# Example

This common use-case
```
unsafe extern "C" {
    fn fill(data: &mut [i32], value: i32);
    fn work(data: &[i32]);
}

pub fn foo() {
    let mut data: [i32; 1 << 12];
    unsafe {
        fill(&mut data, 0);
        work(&data);
    }
}
```
is not supported by Rust:
```
7 |     let mut data: [i32; 1 << 12];
  |         -------- binding declared here but left uninitialized
8 |     unsafe {
9 |         fill(&mut data, 0);
  |              ^^^^^^^^^ `data` used here but it isn't initialized
```
without writing complex `MaybeUninit` logic.

# Optimizations

There is no dedicated auto-init instruction but instructions
that were inserted by auto-init logic are marked with metadata.

Dead assignments to scalars are very cheap and
also well optimized by too many SSA passes to name them
(dce, bdce, adce, instcombine, etc.).

## Optimization of stores

Corresponding optimizations are mainly in LLVM DeadStoreElimination.cpp.
There is also MoveAutoInit.cpp which sinks auto-init closer to uses in CFG;
it's used to avoid initializations in cases like
```
void foo() {
  int a, b;
  ...
  if (error) {
    int buf[99999];
    handle_error(buf);
  }
  ...
}
```
Finally InstCombine and EarlyCSE also do some basic opts.

DSE is based on MemorySSA and has no significant limitations
except for several limiting thresholds.
It has been [significantly improved](https://github.com/llvm/llvm-project/issues/39873)
specifically for auto-init.

Interestingly enough some researches [found](https://users.elis.ugent.be/~jsartor/researchDocs/OOPSLA2011Zero-submit.pdf)
that DSE benefits are very small because duplicating stores
are well optimized at hardware level.

### Analysis method

I looked for relevant passes by selecting shortlist from
```
$ opt -O2 -print-pipeline-passes ...
```
and checking if they can optimize this code
```
declare void @bar(ptr noundef)

define void @foo() {
  %1 = alloca i32, align 4
  store i32 123, ptr %1, align 4
  store i32 256, ptr %1, align 4
  call void @bar(ptr noundef nonnull %1)
  ret void
}
```
(via `opt -passes='PASS' FILE -S -o-`).

Relevant passes: dse, instcombine, early-cse<memssa>

Irrelevant passes: early-cse, simplifycfg, dce, bdce, adce, mem2reg/sroa, gvn

# Workarounds

[Workarounds](survey.md#solutions)) require using
  - `MaybeUninit` types and raw pointers
  - dedicated APIs provided by containers if available

Disadvantage of `MaybeUninit` is that libraries that you use
must support it.

It would help if language(s) type system could express
that function writes certain range of pointer argument
(LLVM already has `readonly` and `writeonly` attributes).

TODO:
  - study critics in https://www.reddit.com/r/rust/comments/1iad0lk/rusts_worst_feature_spoiler_its_borrowedbuf_i/

# Suggested readings

C++:
  - [Killing Uninitialized Memory](https://github.com/microsoft/MSRC-Security-Research/blob/master/presentations/2019_09_CppCon/CppCon2019%20-%20Killing%20Uninitialized%20Memory.pdf) ([video](https://www.youtube.com/watch?v=rQWjF8NvqAU))
  - [Erroneous behavior for uninitialized reads](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p2795r2.html)
  - [SafeInit: Comprehensive and Practical Mitigation of Uninitialized Read Vulnerabilities](https://www.ndss-symposium.org/wp-content/uploads/2017/09/ndss2017_05B-2_Milburn_paper.pdf)
    * [video](https://www.youtube.com/watch?v=qGzB5x3mnXw)

Java:
  - [Why Nothing Matters: The Impact of Zeroing](https://users.elis.ugent.be/~jsartor/researchDocs/OOPSLA2011Zero-submit.pdf)
    (analysis of overheads but not focused on stack inits)

TODO:
  - anything about Rust ?

# Performance impact

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

Results for Clang can be obtained via
```
$ ./llvm-build.sh
$ export MALLOC_MMAP_THRESHOLD_=0
$ valgrind --trace-children=yes --tool=deadwrites build-ref/bin/clang++ -O2 -w -S files-small/LICM.ii
$ valgrind --trace-children=yes --tool=deadwrites build-new/bin/clang++ -O2 -w -S files-small/LICM.ii
```
For llvmorg-20.1.7 I got 2x increase of dead stores under `-ftrivial-auto-var-init`:
  - ref:
    ```
    ==2723404== Detected 11% dead writes (3076342389 out of 25657876716 total)
    ```
  - auto-init:
    ```
    ==2781244== Detected 23% dead writes (7956280742 out of 33419109989 total)
    ```

## Disabling the check

It's not really possible to disable this check per language rules...

## Measurements

Rather than measuring Rust, we compare Clang with and without `-ftrivial-auto-var-init`.
In [Hardening: current status and trends](https://github.com/yugr/slides/blob/main/CppZeroCost/2025/EN.pdf)
the authors reported 4.5% degradation for Clang (compilation of CGBuiltins.ii).

Other forced initialization overheads:
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

According to [Hardening: current status and trends](https://github.com/yugr/slides/blob/main/CppZeroCost/2025/EN.pdf)
similar checks in hardened C++ have on-par overheads:
  - my tests (compiled by Clang 20):
    * ~1.5% Clang
    * ~7% ffmpeg
    * PTS testsuite: apache 1.5%, povray -34%
  - 1% (Firefox with lots of tuning)
  - 1-3% Postgres (up to 20% in some scenarios)
  - virtio, Chrome: up to 10% in some scenarios

(note: for PTS we ignored differences <= 1% due to high noise,
similar to [Exploiting Undefined Behavior in C/C++ Programs for
Optimization: A Study on the Performance Impact](https://web.ist.utl.pt/nuno.lopes/pubs/ub-pldi25.pdf)).

To statically check how many stores can't be eliminated, we compare number
of stores and memsets in loops of Clang compiler.
To generate Clang .bc files, update attached `llvm-build.sh` by adding `-save-temps`
and run it. Then run
```
for B in build-ref build-new; do
  echo "=== $B"
  for f in $B/*.bc; do
    build-bootstrap/bin/opt $f -o opt.bc
    ~/tasks/rust/count-stores/Count opt.bc
  done | awk 'BEGIN{s=0; ms=0} /Loop stats:/{s+=$3; ms+=$5} END{print s " stores, " ms " memsets"}'
done
```
My results are
```
=== build-ref
478006 stores, 1752 memsets
=== build-new
498320 stores, 19362 memsets
```
so +4% stores and 11x (!) memset growth.

TODO:
  - initialize `malloc`-ed data via `LD_PRELOAD` to account for heap inits
    (see [zeralloc](https://github.com/yugr/zeralloc))
