UV [repo](https://github.com/astral-sh/uv)

Built and tested on `dc5b3762f38a8e47b53bec9cc3cefb71e4aef55c` commit.

# Build

Built and tested with `rustc` version `rustc 1.86.0 (05f9846f8 2025-03-31)` and `cargo` version `cargo 1.86.0 (adf9b6ad1 2025-02-28)`

# Run

Create empty python venv in `.venv` subdirectory of the repo: `python3 -m venv .venv`.

Execute `cargo bench` (approx 15m on x86 12-core machine to build and run the benchmarks).
