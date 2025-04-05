use std::hint::black_box;

#[derive(Clone)]
pub struct A {
  pub data: [i32; 1024],
}

pub fn mov(a: A) {
    let a = a;
    black_box(&a);
}

pub fn cop(a: A) {
    let a = a.clone();
    black_box(&a);
}
