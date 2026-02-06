use std::ops::AddAssign;

#[cfg(generic)]
#[inline(never)]
fn foo<T: AddAssign + Copy>(xs: &[T], init: T) -> T
{
    let mut ans = init;
    for x in xs {
        ans += *x;
    }
    ans
}

#[cfg(not(generic))]
#[inline(never)]
fn foo(xs: &[i32], init: i32) -> i32 {
    let mut ans = init;
    for x in xs {
        ans += *x;
    }
    ans
}

mod m1 {
    use foo;
    pub(crate) fn f(a: &[i32]) -> i32 {
        25 + foo(a, 100)
    }
}

mod m2 {
    use foo;
    pub(crate) fn f(a: &[i32]) -> i32 {
        99 + foo(a, 200)
    }
}

mod m3 {
    use foo;
    pub(crate) fn f(a: &[i32]) -> i32 {
        3241 + foo(a, 90)
    }
}

mod m4 {
    use foo;
    pub(crate) fn f(a: &[i32]) -> i32 {
        554 + foo(a, 40)
    }
}

fn main() {
    let v = vec![125; 100];
    let num1 = m1::f(&v);
    let num2 = m2::f(&v);
    let num3 = m3::f(&v);
    let num4 = m4::f(&v);
    println!("Hello, world {}", num1 / num2 * num3 - num4);
}
