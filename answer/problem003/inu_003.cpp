#include <stdio.h>

int main() {

    int num=0;
    int result=0;
    int arr[100][100]={0};
    scanf("%d",&num);


    for(int i=0; i<num; i++){
        for(int j=0; j<num; j++){
            scanf("%d",&arr[i][j]);
        }
    }
    for(int i=0; i<num; i++){
        for(int j=0; j<num; j++){
            printf("%2d ",arr[i][j]);
        }
        printf("\n");
    }

    for(int i=1; i<=num-2; i++){
        result += arr[num-2][i];
        result += arr[1][i];
    }

    for(int i=2; i<=num-3; i++){
        result += arr[i][1];
        result += arr[i][num-2];
    }
    
    printf("%d",result);
    return 0;
}
