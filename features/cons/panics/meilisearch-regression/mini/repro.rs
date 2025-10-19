pub fn foo(cardinality: usize, from: &[u16]) -> Vec<u16> {
    let mut values = vec![0; cardinality as usize];
    values.iter_mut().zip(from.iter()).for_each(|(t, f)| *t = *f);
    values.iter_mut().for_each(|n| *n = u16::from_le(*n));
    values
}
