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

pub fn f1_vec(v: Vec<i32>, n: usize) -> i32 {
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

pub fn f2_vec(v: Vec<i32>, a: usize, b: usize) -> i32 {
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

pub fn f3_vec(v: &mut Vec<i32>, n: usize) {
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

pub fn f4_vec(v: &mut Vec<i32>, a: usize, b: usize) {
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

// 1.87: bounds checks not removed from loop and loop not vectorized
pub fn f8(v: &[i32]) -> i32{
    let mut ans = 0;
    let chunk_len = 4;
    let num_chunks = v.len() / chunk_len;
    for i in 0..num_chunks {
        for j in 0..chunk_len {
            ans += v[i * chunk_len + j];
        }
    }
    ans
}

// 1.87: BCs loop-removed and loop vectorized
pub fn f9(x: &[i32], y: &[i32], z: &mut [i32]) {
    for i in 0..z.len() {
        z[i] = x[i] * y[i];
    }
}

// Convolution-like kernel from https://users.rust-lang.org/t/rust-performance-help-convolution/44075
// 1.87: BCs loop-removed and inner loop vectorized but a lot of checks
pub fn f10(v: &[i32], kernel: &[i32]) -> Vec<i32> {
    assert!(v.len() >= kernel.len());
    let n = v.len() - kernel.len() + 1;
    let mut ans = vec![0; n];
    for i in 0..n {
        let mut acc = 0;
        for j in 0..kernel.len() {
            acc += v[i + j] * kernel[j];
        }
        ans[i] = acc;
    }
    ans
}

extern "C" {
    fn call(i: i32);
}

// A variant of f5
// 1.87: BCs not loop-removed
pub fn f11(v: &[i32], n: usize) {
    unsafe {
        for i in 0..n {
            call(v[i]);
        }
    }
}

// From https://users.rust-lang.org/t/performance-of-iterator-over-for-loops-without-boundry-checks/96162
// 1.87: BCs removed
pub fn f12(s: &[u8]) -> usize {
    let n = s.len();
    'outer: for i in 1..n {
        for j in i..n {
            if s[j] != s[j - i] {
                continue 'outer;
            }
        }
        return i;
    }
    n
}

// From https://www.nickwilcox.com/blog/autovec/
// 1.87: BCs not loop-removed and loop not vectorized
pub fn f13(dst: &mut [i32], src: &[i32], gain_l: i32, gain_r: i32) {
//    let dst = &mut dst[0..2*src.len()];
    for i in 0..src.len() {
        dst[i * 2 + 0] = src[i] * gain_l;
        dst[i * 2 + 1] = src[i] * gain_r;
    }
}

