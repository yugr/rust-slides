This is a simple solution for https://leetcode.com/problems/push-dominoes/description/
which illustrates that `resize + []` is significantly faster than `reserve + push_back`.

$ gcc -O2 bench.cpp

$ time ./a 0
SUCCESS

real    0m1.493s
user    0m1.484s
sys     0m0.031s

Asus@LAPTOP-8ELNT1I2 ~/tasks/leet/push-dominoes/bench
$ time ./a 0
SUCCESS

real    0m1.485s
user    0m1.375s
sys     0m0.124s


$ time ./a 2
SUCCESS

real    0m1.244s
user    0m1.218s
sys     0m0.015s

Asus@LAPTOP-8ELNT1I2 ~/tasks/leet/push-dominoes/bench
$ time ./a 2
SUCCESS

real    0m1.238s
user    0m1.125s
sys     0m0.108s

