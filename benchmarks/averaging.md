Modern CPUs/OSs have high noise levels and even when
actively trying to stabilize them (e.g. see instructions
[here](https://github.com/yugr/uInit)) 1% noise is expected.

A "proper" solution would be to run dozens of experiments and
plot confidence intervals or box/violin plots.
Unfortunately this is not acceptable for macrobenchmarks like SPEC
or our Rust bench suite which take long hours.

For such cases we need to come up with some other solution for noise problem.

Authors of [Exploiting Undefined Behavior in C/C++ Programs for
Optimization: A Study on the Performance Impact](https://dl.acm.org/doi/abs/10.1145/3729260)
simply ignored performance changes which are within 2%.

SPEC rules suggest to [select median](https://www.spec.org/cpu2017/Docs/runrules.html#MedianOrLowerOfTwo)
of benchmarks runs (in hope that it would be more stable than mean)
but this does not make much of a difference in practice.

Many authors suggest to select minimum of measurements
as this should be closer to "real" runtime
(undamaged by system jitter) e.g.
  - [Benchmarking: minimum vs average](https://blog.kevmod.com/2016/06/10/benchmarking-minimum-vs-average/)
    * demostrates how minimum is a more stable statistic for right-skewed distributions
  - [easyperf blog: Benchmarking: compare measurements and check which is faster](https://easyperf.net/blog/2019/12/30/Comparing-performance-measurements)
    * advocates for minimum for small samples
  - [The mean misleads: why the minimum is the true measure of a function’s run time](https://medium.com/better-programming/the-mean-misleads-why-the-minimum-is-the-true-measure-of-a-functions-run-time-47fa079075b0)
    * shows how mins have much lower variance for significantly right-skewed distros
  - [The mean misleads, part 2: more data for the doubters](https://medium.com/better-programming/the-mean-misleads-part-ii-more-data-for-the-doubters-7f11881f7337)
    * shows that mins are preferred for typical benchmarks for smaller samples
  - [Daniel Lemire's blog: Are your memory-bound benchmarking timings normally distributed?](https://lemire.me/blog/2023/04/06/are-your-memory-bound-benchmarking-timings-normally-distributed/)

It is not clear how stable minimum is more stable than mean across runs though.

Also this solution won't work if there is some some intrinsic randomization
in test itself e.g. HashMap randomization in Rust programs (see
https://internals.rust-lang.org/t/support-turning-off-hashmap-randomness/19234
for details).
