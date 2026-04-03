#include <stdio.h>

int main(){
    int a,b,c;

    scanf("%d", &c);

    for(a=1;a<=9;a++){
        for(b=1;b<=9;b++){
            printf("%dx%d=%d\n",a,b,a*b);
        }
        printf("\n");
    }
     return 0;
}