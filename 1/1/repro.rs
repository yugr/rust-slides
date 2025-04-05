use std::hint::black_box;

#[derive(Clone)]
pub struct A {
  pub data: [i32; 1024],
}

pub fn mov(a: A) {
    let a1 = a;
    let a2 = a1;
    black_box(&a2);
}

pub fn cop(a: A) {
    let a1 = a.clone();
    let a2 = a1.clone();
    black_box(&a2);
}
