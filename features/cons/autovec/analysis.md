Autovec is not really pros or cons, just an optimization which can be negatively
(or positively) affected by other language features
(currently bounds checking and lack of fast math).
We should study and measure these effects while investigating said features.

The only thing worth discussing here is helping compiler to autovectorize
by structuring the code appropriately.

TODO:
  - investigate suggestions here (`exact_chunks`, `chunks_exact`, etc.):
    * https://www.reddit.com/r/rust/comments/1ha7uyi/memorysafe_png_decoders_now_vastly_outperform_c/
    * https://coaxion.net/blog/2018/01/speeding-up-rgb-to-grayscale-conversion-in-rust-by-a-factor-of-2-2-and-various-other-multimedia-related-processing-loops
    * https://tweedegolf.nl/en/blog/153/simd-in-zlib-rs-part-1-autovectorization-and-target-features
    * https://emschwartz.me/unnecessary-optimization-in-rust-hamming-distances-simd-and-auto-vectorization
