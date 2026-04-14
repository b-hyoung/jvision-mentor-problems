#include <stdio.h>
int main(){

int arr[100][100]={0};
int num=0;
int result=0;
printf("숫자 입력:\n");
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
printf("\n\n");
}
for(int u=1; u<num-1; u++){
result+=arr[1][u];
result+=arr[u][1];

}
for(int n=2; n<num-2; n++){
result+=arr[n][1];
result+=arr[n][num-2];
}
printf("두번째 껍데기 값:");
printf("%d",result);
//좌측 상단 1,1
//좌측 하단 1,num-2
//우측 상단 num-2,1
//우측 하단 num-2,num-2
return 0;
}
