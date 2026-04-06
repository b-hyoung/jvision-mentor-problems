#include <stdio.h>

int main() {
    int N;
    printf("1부터 100까지 중의 정수를 입력하세요 : \n");
    scanf("%d",&N);
    for(int i = 1; i<=N; i++){
        for (int j = 0; j < i; j++){
            printf("*");
        }
        printf("\n");
    }
    return 0;
}
