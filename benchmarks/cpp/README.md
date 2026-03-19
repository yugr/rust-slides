A bunch of scripts to run different C++ benchmarks.

Once the data is collected, plots can be built via something like
```
$ benchmarks/cpp/plots.py --font-size=14 \
  --average-mode median \
  --pts-dir hertz/PTS/results-1 --pts-dir hertz/PTS/results-2 \
  --ffmpeg-dir hertz/ffmpeg-bench/results-1 --ffmpeg-dir hertz/ffmpeg-bench/results-2 --ffmpeg-dir hertz/ffmpeg-bench/results-3 \
  --llvm-dir hertz/llvm-bench/results-1 --llvm-dir hertz/llvm-bench/results-2 \
  AutoInit
```
