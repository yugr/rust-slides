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

Another example is developing analog of `std::find`
[here](https://hackernoon.com/this-tiny-rust-tweak-makes-searching-a-slice-9x-faster):
branchless code
```
    for (i, &b) in haystack.iter().enumerate().rev() {
        if b == needle {
            position = Some(i);
        }
    }
```
fails to vectorize but `chunks_exact` helps:
```
fn find_no_early_returns(haystack: &[u8], needle: u8) -> Option<usize> {
    return haystack.iter().enumerate()
        .filter(|(_, &b)| b == needle)
        .rfold(None, |_, (i, _)| Some(i))
}

fn find(haystack: &[u8], needle: u8) -> Option<usize> {
    let chunks = haystack.chunks_exact(32);
    let remainder = chunks.remainder();
    chunks.enumerate()
        .find_map(|(i, chunk)| find_no_early_returns(chunk, needle).map(|x| 32 * i + x) )
        .or(find_no_early_returns(remainder, needle).map(|x| (haystack.len() & !0x1f) + x))
}
```
