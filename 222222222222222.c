#include <stdio.h>

int main(){
    int n;
    scanf("%d", &n);

    int num[n][n];
    int sum = 0;

    for(int i=0; i<n; i++){
        for(int j=0; j<n; j++){
            scanf("%d", &num[i][j]);
        }
    }

    for(int i=0; i<n; i++){
        for(int j=0; j<n; j++){
            if(i>=1 && i<=n-2 && j>=1 && j<=n-2){
                if(i==1 || j==1 || i==n-2 || j==n-2){
                sum+=num[i][j];
                }
            }
        }
    }

    printf("%d\n", sum);
    return 0;
}