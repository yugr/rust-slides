extern "Rust" {
    fn bar(x: [String; 100]) -> usize;
}

pub unsafe fn foo(x: [String; 100]) -> usize {
    bar(x)
}
