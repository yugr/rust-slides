#[no_mangle]
pub fn foo(v: &[i32], k: usize, n: usize) -> i32 {
    let mut ans = 0;
    for i in 0..n {
        ans += v[i ^ k];
    }
    ans
}
