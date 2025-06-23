Autovec is not really pros or cons, just an optimization which can be negatively
(or positively) affected by other language features
(currently bounds checking, lack of fast math and noalias).
We should study and measure these effects while investigating said features.

The only thing worth discussing here is helping compiler to autovectorize
by structuring the code appropriately.

Many people suggest to use explicit `chunks_exact` to help autovec.
In particular [Rust png library](https://github.com/image-rs/image-png)
uses this approach extensively: the original scalar code
```
    x
        .iter()
        .zip(y.iter())
        .map(|(&x_val, &y_val)| {
            (x_val ^ y_val).count_ones()
        })
        .sum::<u32>();
```
is replaced with explicit chunks:
```
    x
        .chunks_exact(8)
        .zip(y.chunks_exact(8))
        .map(|(x_chunk, y_chunk)| {
            let x_val = u64::from_ne_bytes(x_chunk.try_into().unwrap());
            let y_val = u64::from_ne_bytes(y_chunk.try_into().unwrap());
            (x_val ^ y_val).count_ones()
        })
        .sum::<u32>();
```

TODO:
  - more use-cases for `chunks_exact`
