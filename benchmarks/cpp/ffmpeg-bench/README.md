Based on benchmark from https://zatoichi-engineer.github.io/2017/10/04/stack-smashing-protection.html#performance-cost

Download ffmpeg from https://ffmpeg.org/releases/ffmpeg-8.0.1.tar.xz
and x264 from https://code.videolan.org/videolan/x264.git (I used 0480cb05) and
install nasm and pkgconf.

Build LLVM compiler as in llvm-bench.

Then run ffmpeg benchmarks via
```
PATH=$INSTALL_DIR:$PATH ./run.sh --ffmpeg path/to/ffmpeg --x264 path/to/x264 configs.txt
```

Data can then be averaged via
```
for file in results/*.log; do echo $file; cat $file | sed -ne '/user/{s/user.*//; p}' | Median; done
```
