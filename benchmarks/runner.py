import subprocess
from pathlib import Path
import argparse

benches_info = {
    "bevy-bencher": ("", "cargo bench"),
    "zed": ("crates/rope", "cargo bench"),
    "zed": ("crates/extension_host", "cargo bench"),
    "veloren": ("", "cargo bench"),
    "uv": ("", "cargo bench --no-fail-fast"),
    "tokio": ("", "cargo bench"),
    "SpacetimeDB": (
        "crates/bench",
        "cargo bench --bench generic --bench special --no-fail-fast",
    ),
    "ruff": ("crates/ruff_benchmark", "cargo bench"),
    "rav1e": ("", "cargo criterion --features=bench"),
    "oxipng": ("", "cargo bench"),
    "meilisearch": ("", "cargo bench"),
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t", "--toolchain", help="toolchain version to use", default=None
    )
    parser.add_argument(
        "-p", "--path", help="Path to repos with benchmarks", default="./"
    )
    parser.add_argument(
        "-b",
        "--build-only",
        dest="build_only",
        action="store_true",
        help="Operation to perform in repos",
    )
    parser.add_argument(
        "-c",
        "--clean",
        dest="clean",
        action="store_true",
        help="Clean repositores before running",
    )

    parser.add_argument(
        "-r",
        "--run-options",
        dest="run_options",
        default="taskset 0x1 nice -n -20 setarch -R",
    )
    args = parser.parse_args()

    base_path = Path(args.path)

    for bench_repo, bench_params in benches_info.items():
        bench_path = base_path / bench_repo / bench_params[0]
        cargo_args = bench_params[1].split()
        if args.toolchain is not None:
            insert_idx = cargo_args.index("cargo") + 1
            cargo_args.insert(insert_idx, "+" + args.toolchain)
        cargo_args.append("--no-run")
        if args.clean:
            subprocess.run(
                ["cargo", "clean"],
                check=True,
                capture_output=False,
                cwd=str(bench_path),
            )
        subprocess.run(
            cargo_args, check=True, capture_output=False, cwd=str(bench_path)
        )

    if args.build_only:
        return

    for bench_repo, bench_params in benches_info.items():
        print(f"Benching {bench_repo}")
        bench_path = base_path / bench_repo / bench_params[0]
        cargo_args = args.run_options.split()
        cargo_args.extend(bench_params[1].split())
        if args.toolchain is not None:
            insert_idx = cargo_args.index("cargo") + 1
            cargo_args.insert(insert_idx, "+" + args.toolchain)
        subprocess.run(
            cargo_args, check=True, capture_output=False, cwd=str(bench_path)
        )


if __name__ == "__main__":
    main()
