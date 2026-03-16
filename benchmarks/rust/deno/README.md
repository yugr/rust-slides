# Build

Built and tested with `rustc` version `rustc 1.86.0 (05f9846f8 2025-03-31)` (stable) and `cargo` version `cargo 1.86.0 (adf9b6ad1 2025-02-28)`

- Follow the official [build guide](https://docs.deno.com/runtime/contributing/building_from_source/) to install all the needed dependencies.
- If you encounter errors with `--export-dynamic-symbol-list` flag, your system linker is too old (e.g. `ld` version 2.34 does not recognize this flag, but `lld-19` does). This problem can be circumvented by applying [this patch](Remove-new-linker-flag.patch) to the repo.

# Run

`deno bench` can be used to run some `*.ts` benchmark and test files (they seem to be spead throughout the repository), but no easy way to run a full benchmark suite was found
