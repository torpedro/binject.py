
#include <unistd.h>
#include <stdio.h>
#include <string>
#include <cstdlib>
#include <iostream>

/**
 * sums up all numbers from 1 to n
 */
long sum(int n) {
    long result = 0;
    for (int i = 1; i <= n; ++i) {
        result += i; // <inject-skip>
    }

    if (n % 2 == 1) {
        printf("fault\n"); // <inject-fault>
    }
    return result;
}




int main(int argc, char const *argv[]) {
    printf("PID: %u\n\n", getpid());
    // int x = 0;
    // const char* y = "abcd";
    // double z = 2312;
    // printf("%d\n", x);
    // printf("%s\n", y); 
    // printf("%.2f\n", z); 

    int input = 1;
    while (input > 0) {
        printf("Enter a number: "); fflush(stdout);
        std::cin >> input;
        printf("Sum of %d: %ld\n\n", input, sum(input));
    }

    return 0;
}

