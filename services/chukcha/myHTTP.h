//
// Created by shtrikh17 on 21.01.18.
//

#ifndef SIMPLEHTTPSERVER_MYHTTP_H
#define SIMPLEHTTPSERVER_MYHTTP_H

#include <stdlib.h>
#include <unistd.h>
#include <sys/stat.h>
#include "commonOperations.h"

typedef struct{
    char* key;
    char* value;
} HTTP_header;

typedef struct{
    char* method;
    char* path;
    char* protocol;
    int nHeaders;
    HTTP_header* headers;
    char* body;
    char* fullPath;
} HTTP_request;

typedef struct{
    char* protocol;
    int code;
    char* description;
    int nHeadres;
    HTTP_header* headers;
    char* body;
} HTTP_response;

typedef struct{
    char* contents;
    struct RESULT* next;
} RESULT;

HTTP_request* parseRequest(char* request);
int handle_HTTP_request(char* req, char** response, char* rootDir);



#endif //SIMPLEHTTPSERVER_MYHTTP_H
