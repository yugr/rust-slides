Various useful info about Rust compiler building, testing, etc.

# Local install

Use [rustup](https://rustup.rs/) but set
```
export RUSTUP_HOME=path/to/rustup/cache
export CARGO_HOME=path/to/cargo/and/rustc
```

# Building compiler

See [Dev Guide](https://rustc-dev-guide.rust-lang.org/building/how-to-build-and-run.html)
but generally it's just
```
$ ./x setup  # Select 'compiler'
```

Then add to `bootstrap.toml`
```
[rust]
channel = "nightly"
```
to build a nightly compiler (some benches use features which are unstable in 1.87 and will not compile with the default `dev` channel).

Add
```
[llvm]
assertions = true
```
for debug prints in LLVM and build stage1 compiler:
```
$ ./x build -jN library
```
(set `N` according to your quota).

Default settings (in `src/bootstrap/src/core/config/config.rs`) are reasonable:
  - build optimized compiler and std
  - no incremental build
  - default codegen units for std (16 ?)
    * this is overridden in `src/ci/run.sh`
  - no overflow checks unless debug
  - build std with `panic_unwind`

Disk consumption:
  - sources: 750M
  - release build: 10G

## Prebuilt LLVM

Since Sep 16 this will fail because CI LLVM build for acaea3d2 of https://github.com/rust-lang/llvm-project was removed from server:
```
downloading https://ci-artifacts.rust-lang.org/rustc-builds/2848101ed585d93075013ab652ef82e1991b8a4d/rust-dev-nightly-x86_64-unknown-linux-gnu.tar.xz
curl: (22) The requested URL returned error: 404
Warning: Problem (retrying all errors). Will retry in 1 seconds. 3 retries
Warning: left.
curl: (22) The requested URL returned error: 404
Warning: Problem (retrying all errors). Will retry in 2 seconds. 2 retries
Warning: left.
curl: (22) The requested URL returned error: 404 #
Warning: Problem (retrying all errors). Will retry in 4 seconds. 1 retries
Warning: left.
curl: (22) The requested URL returned error: 404             #

ERROR: failed to download llvm from ci

    HELP: There could be two reasons behind this:
        1) The host triple is not supported for `download-ci-llvm`.
        2) Old builds get deleted after a certain time.
    HELP: In either case, disable `download-ci-llvm` in your bootstrap.toml:

    [llvm]
    download-ci-llvm = false
```
You can instead download it from https://github.com/yugr/rustc-builds and
untar to `build/x86_64-unknown-linux-gnu/ci-llvm`.

# Rebuilding LLVM

To build LLVM for Rust add
```
[llvm]
download-ci-llvm = false
link-shared = true
targets = "X86"
experimental-targets = ""
```
and either
```
release-debuginfo = true
```
or
```
optimize = false
```

# Using built compiler

Register toolchain with `rustup`:
```
$ rustup toolchain link MY_TOOLCHAIN_NAME build/host/stage1
```

If needed, make it default via
```
$ rustup default stage1
```

# Dump rustc invocations

Just add `--verbose` to cargo args.

To reproduce `rustc` call locally may need some env. variables
e.g. for meilisearch I had to
```
export CARGO_MANIFEST_DIR=/home/yugr/tasks/rust/bench/meilisearch-new-new/target/release/deps
export CARGO_PKG_VERSION_MAJOR=1
export CARGO_PKG_VERSION_MINOR=0
export CARGO_PKG_VERSION_PATCH=0
```

# Patch dependency

To force cargo to use local (patched) copy of some dependency
(for current package and all it's deps too), add something like
```
[patch.crates-io]
roaring = { path = "/home/yugr/tasks/rust/bench/mod/roaring-0.10.12" }
```
to Cargo.toml.

# Debug logs

To print compiler debug log run it with
```
RUSTC_LOG=debug
```

Optimized MIR can be dumped with `--emit mir`
(add `-Zmir-opt-level=0` for unoptimized).
To dump MIR after each transform (to `mir_dump/`), run with `-Zdump-mir=FUNC_NAME`.
Individual transforms can be disabled via `-Zmir-enable-passes=-PASS_NAME_1,-PASS_NAME_2`.

To dump _optimized_ LLVM IR use `--emit llvm-ir`.
To print intermediate IRs use `-Cllvm-args='-print-after-all`.
