#include <stdio.h>

int main(){
    int N = 0;
    printf("만들 별의 개수를 입력하시오.\n");
    scanf("%d",&N);
                                                         
    for(int i=1; i<=N; I++){             
        for(int j=1; j<i; j++){
            printf("*");
        }
        printf("\n")
    }
    
    return 0;
}
