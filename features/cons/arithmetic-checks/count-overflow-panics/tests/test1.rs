#[no_mangle]
fn foo(mut x: i32, y: i32) -> i32 {
  x += y;
  x += y;
  x
}
