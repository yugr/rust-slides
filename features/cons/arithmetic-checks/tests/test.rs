#[no_mangle]
pub fn foo_1(x: i32, y: i32) -> i32 {
    // Division by zero + overflow checks
    x / y
}

#[no_mangle]
pub fn foo_2(x: u32, y: u32) -> u32 {
    // Only division by zero check
    x / y
}

#[no_mangle]
pub fn foo_3(x: f32) -> i32 {
    // Saturating cast by default, simple cast with -Zsaturating-float-casts=off
    x as i32
}

#[no_mangle]
pub fn foo_4(x: i64) -> i32 {
    // No checks regardless of flags
    x as i32
}

#[no_mangle]
pub fn foo_5(x: i32, y: i32) -> i32 {
    // No checks by default, ovf check with -C overflow-checks=on
    x + y
}

#[no_mangle]
pub fn foo_6(x: i32, y: u32) -> i32 {
    // No checks by default, ovf check with -C overflow-checks=on
    x << y
}
