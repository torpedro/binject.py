
#include <stdio.h>





int main(int argc, char const *argv[]) {


	int x = 0;
	const char* y = "abcd";
	double z = 2312;

	printf("%d\n", x);
	printf("%s\n", y); // <inject-fault>
	printf("%.2f\n", z);


	return 0;
}

