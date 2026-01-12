#include <iostream>
#include <ctime>
#include <map>
#include <unordered_map>
using namespace std;

template<typename T>
void f() {
    clock_t start = clock(); 
    T m;
    for (int i = 0; i < 200000000; ++i) {
        auto j = i % 100000;
        auto pos = m.find(j);
        if (pos == m.end()) m[j] = 1;
        else ++pos->second;
    }
    cout << m[40000] << " " << float(clock() - start)
        / CLOCKS_PER_SEC << " s" << endl;    
}

int main() {
    f<map<unsigned int, unsigned int>>();
    f<unordered_map<unsigned int, unsigned int>>();
}
