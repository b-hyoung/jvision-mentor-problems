#include <stdio.h>

int main() {
    
    int i=0,j=0,n;
    scanf("%d",&n);
    int start =n, end =n+1;
    for(i=0;i<n;i++){
        for(j=0;j<start;j++){
            printf(" ");
        }
        for(j=start;j<end;j++){
            printf("*");
        }
 		start--;
 		end++;
        printf("\n");
    }

    return 0;
}
