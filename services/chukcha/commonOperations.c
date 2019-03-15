//
// Created by shtrikh17 on 21.01.18.
//

#include "commonOperations.h"

void printLog(char* p){
#ifdef DEBUG
    FILE* f = fopen("server.log", "a+");
    fprintf(f, "%s\n", p);
    fclose(f);
#endif
}

char** split_c_string(char* string, char* delimiter, int* num){
    int len = strlen(string);
    int dlen = strlen(delimiter);
    int nTokens = 0;
    for(int i=0; i<len; i++){
        if(strncmp(string+i, delimiter, dlen)==0){
            nTokens++;
            i = i + dlen - 1;
        }
    }
    nTokens++;
    char** result = (char**) malloc (nTokens*sizeof(char*));

    char* currentToken = string;
    int N = 0;
    for(int i=0; i<len; i++){
        if(strncmp(string+i, delimiter, dlen)==0){
            if(currentToken!=string+i){
                result[N] = currentToken;
            }
            N++;
            for(int j=0; j<dlen; j++) {
                *(string+i+j) = '\0';
            }
            currentToken = string+i+dlen;
        }
    }
    if(*currentToken!='\0'){
        result[N] = currentToken;
        N++;
    }

    *num = N;
    return result;
}
