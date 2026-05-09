#include <stdio.h>
#include <stdbool.h>
#include <string.h>

bool solution(const char* s){
    int size = strlen(s);
    int num = 0;
    for(int i=0; i<size; i++){
        if(s[i]=='('){
            num += 1;
        }
        else{
            num -= 1;
        }
        if(num<0){
            return false;
        }
    }
    if(s[0] == ')' || s[0] == s[size-1] || num!=0){
        return false;
    }
    else{
        return true;
    }
}
