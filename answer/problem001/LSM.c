#include <stdio.h>

int main() {
    int i,a=0;
    for(i=1;i<=9;i++){
        a=i*9;
        printf("9x%d = %d\n" ,i,a);
    }
    return 0;
}