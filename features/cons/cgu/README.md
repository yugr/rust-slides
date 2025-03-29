Rust uses the concept of codegen units (CGUs) to parallelize compilation of crates and significantly reduce build times (16-32 cgus is the default value). However, splitting the program into several independent compilation units prevents some optimizations on the boundary between the units:

 - Inlining requires explicit annotation and link-time optimization (but is still not perfect with these solutions) (https://github.com/wasmi-labs/wasmi/issues/339#issuecomment-1023034031)
 - Dead code elimination is unable to detect dead loops if they are split over multiple CGUs (https://github.com/rust-lang/rust/issues/57235#issuecomment-450673756)
 - CGUs cause vtable duplication (but vtables in different CGUs are not always equal) which causes some pointer comparisons to be unpredictable (https://github.com/rust-lang/rust/issues/46139)
