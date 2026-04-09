#include <stdio.h>

int main(){
	
	int i,j,n;
	int a = 0,p = 0, f = 0;
	scanf("%d",&n);
	int end = n -1;
	int q[100][100]={0};
	for(i=0;i<n;i++){
		for(j=0;j<n;j++){
			scanf("%d",&q[i][j]);
		}
	}
	
	for(i=1;i<end;i++){
		p = p + q[i][1] + q[i][end-1];
	}
	
	for(j=2;j<end-1;j++){
		f = f + q[1][j] + q[end-1][j];
	}
	
	a = p + f;
	printf("%d",a);
	
	return 0;
}


