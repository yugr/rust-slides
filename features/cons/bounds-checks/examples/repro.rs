// Compiler versions:
// 1.50 - 2021
// 1.70 - June 2023
// 1.80 - July 2024
// 1.87 - May 2025

// 1.70-1.87: bounds checks loop-removed + vectorized without --emit=asm (due to cgu=1)
// 1.70-1.81: bounds checks NOT loop-removed + NOT vectorized with --emit=asm (due to cgu=1)
// 1.50: bounds checks NOT loop-removed + NOT vectorized
pub fn f1(v: &[i32], n: usize) -> i32 {
    let mut ans = 0;
    for i in 0..n {
        ans += v[i];
    }
    ans
}

// 1.70-1.87: bounds checks loop-removed + vectorized
// 1.50: bounds checks NOT loop-removed + NOT vectorized
pub fn f2(v: &[i32], a: usize, b: usize) -> i32 {
    let mut ans = 0;
    for i in a..b {
        ans += v[i];
    }
    ans
}

// 1.70-1.87: bounds checks loop-removed + vectorized
// 1.50: bounds checks NOT loop-removed + NOT vectorized
pub fn f3(v: &mut [i32], n: usize) {
    for i in 0..n {
        v[i] = i as i32;
    }
}

// 1.70-1.87: bounds checks loop-removed + vectorized
// 1.50: bounds checks NOT loop-removed + NOT vectorized
pub fn f4(v: &mut [i32], a: usize, b: usize) {
    for i in a..b {
        v[i] = i as i32;
    }
}

// This function of course is not optimized
pub fn f5(v: &mut [i32], n: usize) -> i32 {
    let mut ans = 0;
    for i in 0..n {
        ans += v[std::hint::black_box(i)];
    }
    ans
}

// More complex index arithmetic => BCs not loop-removed and loop not vectorized (even in 1.87).
// Similar cases e.g. binary heaps.
pub fn f6(v: &mut [i32], n: usize) {
    for i in 0..(n / 2) {
        let l = i;
        let r = n - i - 1;
        v.swap(l, r);
    }
}

// 1.70-1.87: BCs loop-removed and loop vectorized (at least w/o `--emit=asm`)
pub fn f7(v: &[i32], w: &[i32]) -> i32 {
    let mut ans = 0;
    let n = v.len();
    for i in 0..n {
        ans += v[i] * w[i];
    }
    ans
}
