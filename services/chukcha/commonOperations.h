//
// Created by shtrikh17 on 21.01.18.
//

#ifndef SIMPLEHTTPSERVER_COMMONOPERATIONS_H
#define SIMPLEHTTPSERVER_COMMONOPERATIONS_H

#include <string.h>
#include <stdlib.h>
#include <stdio.h>

#define DEBUG

void printLog(char* p);

char** split_c_string(char* string, char* delimiter, int* num);


#endif //SIMPLEHTTPSERVER_COMMONOPERATIONS_H
