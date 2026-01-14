use std::collections::BTreeMap;

const MAX: usize = 50_000_000;

fn main() {
    let mut m = BTreeMap::new();

    for i in 0..MAX {
        m.insert(2 * i, i);
    }

    let mut result: usize = 0;
    for i in 0..MAX {
        match m.get(&i) {
            Some(&val) => result = result.wrapping_add(val),
            None => (),
        }
    }

    println!("{}", result);
}
