Rust uses the concept of codegen units (CGUs) to parallelize compilation of crates and significantly reduce build times (16-32 cgus is the default value). However, splitting the program into several independent compilation units prevents some optimizations on the boundary between the units:

 - Inlining requires explicit annotation and link-time optimization (but is still not perfect with these solutions)
 - Dead code elimination is unable to detect dead loops if they are split over multiple CGUs
 - CGUs cause vtable duplication (but vtables in different CGUs are not always equal) which causes some pointer comparisons to be unpredictable
