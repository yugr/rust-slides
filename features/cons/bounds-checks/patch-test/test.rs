#[no_mangle]
pub fn f0(v: &[i32], i: usize) -> i32 {
    unsafe { *v.get_unchecked(i) }
}

#[no_mangle]
pub fn f1(v: &[i32], i: usize) -> i32 {
    v[i]
}

#[no_mangle]
pub fn f1_vec_ref(v: &Vec<i32>, i: usize) -> i32 {
    v[i]
}

#[no_mangle]
pub fn f1_vec(v: Vec<i32>, i: usize) -> i32 {
    v[i]
}

#[no_mangle]
pub fn f2(v: &[i32], i: usize, j: usize) -> &[i32] {
    &v[i..j]
}

#[no_mangle]
pub fn f2_vec_ref(v: &Vec<i32>, i: usize, j: usize) -> &[i32] {
    &v[i..j]
}

#[no_mangle]
pub fn f3(v: &[i32], i: usize, j: usize) -> &[i32] {
    &v[i..=j]
}

#[no_mangle]
pub fn f3_vec_ref(v: &Vec<i32>, i: usize, j: usize) -> &[i32] {
    &v[i..=j]
}
