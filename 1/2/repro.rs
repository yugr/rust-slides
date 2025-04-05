use std::hint::black_box;

#[derive(Clone)]
pub struct A {
  pub data: [i32; 1024],
}

extern "C" {
    fn foo() -> A;
}

pub fn param(a: A) {
    black_box(a);
}

pub fn ret() -> A {
    unsafe { foo() }
}
