#include <stdio.h>
int main(){

    int num=0;
    printf("피라미드의 높이를 입렵하시오.\n");
    scanf("%d",&num);

    for(int i=1; i<=num*2; i+=2){
        for(int k=num; k*2>i; k--){
            printf(" ");
        }
        for(int j=0; j<i; j++){
            printf("*");
        }
        printf("\n");
    }

    return 0;
}
