To avoid UB Rust inserts checks to saturate FP values to range of integer type
when casting fp to int.

The overhead is significant:
```
pub fn square(num: f32) -> i32 {
    num as i32
}
```
compiles to
```
.LCPI0_0:
        .long   0x4effffff
square:
        cvttss2si       eax, xmm0
        ucomiss xmm0, dword ptr [rip + .LCPI0_0]
        mov     ecx, 2147483647
        cmovbe  ecx, eax
        xor     eax, eax
        ucomiss xmm0, xmm0
        cmovnp  eax, ecx
        ret
```
instead of just
```
square:
        cvttss2si       eax, xmm0
        ret
```
(which can be obtained with `-Zsaturating-float-casts=off`).

In practice some workloads [regress by 20%](https://internals.rust-lang.org/t/help-us-benchmark-saturating-float-casts/6231/14).

There is (unsafe) `to_int_unchecked` API to avoid overhead.

# TODO

* Benchmark relevant projects with disabled saturation (`-Zsaturating-float-casts=off`)
