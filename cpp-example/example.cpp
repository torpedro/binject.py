
#include <stdio.h>
#include <string>
#include <cstdlib>

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

	int x = 0;
	const char* y = "abcd";
	double z = 2312;

	printf("%d\n", x);
	printf("%s\n", y); 
	printf("%.2f\n", z); 

	for (int i = 1; i < argc; ++i) {
		int input = atoi(argv[i]);
		printf("Sum of %d: %ld\n", input, sum(input));
	}

	return 0;
}

