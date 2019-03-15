//
// Created by shtrikh17 on 21.01.18.
//

#include "myHTTP.h"

HTTP_request* parseRequest(char* request){
    int N, nHeadres;
    int k = strlen(request);
    char** head_and_body = split_c_string(request, "\r\n\r\n", &N);
    if(N<1)
        return NULL;
    HTTP_request* http_request = (HTTP_request*) malloc (sizeof(HTTP_request));
    if(N>1)
        http_request->body = head_and_body[1];
    else
        http_request->body = NULL;

    char** headers = split_c_string(head_and_body[0], "\r\n", &nHeadres);
    char** reqType = split_c_string(headers[0], " ", &N);
    http_request->method = reqType[0];
    http_request->protocol = reqType[N-1];
    http_request->path = reqType[1];
    for(int j=1; j<N-2; j++){
        int c = 0;
        while(reqType[j][c]!=0) {
            c++;
        }
        while(reqType[j][c]==0){
            reqType[j][c]=' ';
            c++;
        }
    }
    //http_request->path = split_c_string(reqType[1], "?", &N)[0];
    http_request->path = reqType[1];

    http_request->nHeaders = nHeadres-1;
    http_request->headers = (HTTP_header*) malloc ((nHeadres-1)*sizeof(HTTP_header));
    for(int j=1; j<nHeadres; j++){
        char** header = split_c_string(headers[j], ": ", &N);
        http_request->headers[j-1].key = header[0];
        http_request->headers[j-1].value = header[1];
        free(header);
    }

    free(head_and_body);
    free(headers);
    free(reqType);

    return http_request;
}

int handle_get_request(HTTP_request* request, HTTP_response* response){
    response->headers[response->nHeadres].key = "Content-Type";
    response->headers[response->nHeadres].value = "text/html";
    response->nHeadres++;
    response->body = NULL;
    // Проверка на существование файла - F_OK
    if(access(request->fullPath, F_OK)==0){

        FILE* f = fopen(request->fullPath, "r");
        // Запрещенный к открытию файл не откроется
        if(f==NULL){
            response->code = 403;
            response->description = "FORBIDDEN";
        }
        else{

            struct stat st;
            fstat(fileno(f), &st);
            long fileSize = st.st_size;

            //fseek(f, 0, SEEK_END);
            //long fileSize = ftell(f);
            //fseek(f, 0, SEEK_SET);
            response->body = (char*) malloc (fileSize+1);



            // Упрощенный подход - лучше не читать файл в память, это слишком замедляет сервер
            fread(response->body, 1, fileSize, f);
            response->body[fileSize] = '\0';
            fclose(f);

            response->headers[response->nHeadres].key = "Content-Length";
            char buf[20];
            int N = sprintf(buf, "%d", fileSize)+1;
            response->headers[response->nHeadres].value = (char*) malloc (N);
            strcpy(response->headers[response->nHeadres].value, buf);
            response->nHeadres++;

            response->code = 200;
            response->description = "OK";
        }
    }
    else{
        response->description = "NOT FOUND";
        response->code = 404;
    }
    return 0;
}

int handle_size_request(HTTP_request* request, HTTP_response* response){

    response->headers[response->nHeadres].key = "Content-Type";
    response->headers[response->nHeadres].value = "text/html";
    response->nHeadres++;
    response->body = NULL;
    // Проверка на существование файла - F_OK
    //if(access(request->fullPath, F_OK)==0){

        FILE* fp;
        char* result = (char*)malloc(1024);
        char* command = (char*)malloc(1024);
        strcpy(command, "ls -lh ");
        strcat(command, request->fullPath);
        strcat(command, " | cut -d \" \" -f 5");
        int count = 0;
        RESULT* res = NULL;
        RESULT* cur = NULL;
        int Length = 0;

        fp = popen(command, "r");
        if(fp==NULL){
            printLog("Error getting size");
            free(command);
            free(result);
            return 1;
        }

        while(fgets(result, sizeof(result)-1, fp)!=NULL){
            if(res==NULL){
                res = (RESULT*) malloc(sizeof(RESULT));
                cur = res;
            }
            else{
                cur->next = (RESULT*) malloc(sizeof(RESULT));
                cur = cur->next;
            }
            cur->contents = (char*) malloc(strlen(result)+1);
            cur->next = NULL;
            strcpy(cur->contents, result);
            count += 1;
            Length += strlen(result);
        }

        pclose(fp);
        response->body = (char*) malloc(Length+1);
        cur = res;
        char* t = response->body;
        for(int j=0; j<count; j++){
            sprintf(t, cur->contents);
            t = t + strlen(cur->contents);
            free(cur->contents);
            cur = cur->next;
            free(res);
            res = cur;
        }


        response->headers[response->nHeadres].key = "Content-Length";
        char buf[20];
        int N = sprintf(buf, "%d", Length)+1;
        response->headers[response->nHeadres].value = (char*) malloc (N*sizeof(char));
        strcpy(response->headers[response->nHeadres].value, buf);
        response->nHeadres++;

        response->code = 200;
        response->description = "OK";
    free(command);
    free(result);
  //  }
   /* else{
        response->description = "NOT FOUND";
        response->code = 404;
    }*/
    return 0;
}

int check_and_copy(HTTP_request* request, int j){
    int foundType = 0;
    char type[16];
    if(!strcmp(request->headers[j].key, "Type")){
        strcpy(type, request->headers[j].value);
        if(!strcmp(type, "text/html") || !strcmp(type, "text/text")){
            foundType = 1;
        }
    }

   return foundType;
}

int handle_put_request(HTTP_request* request, HTTP_response* response){
    //if(request->body!=NULL)
    //    printf(request->body);



    int foundType = 0;
    for(int j = 0; j<request->nHeaders; j++){
        foundType = check_and_copy(request, j);
        if(foundType)
            break;
    }


    response->headers[response->nHeadres].key = "Content-Type";
    response->headers[response->nHeadres].value = "text/html";
    response->nHeadres++;
    response->body = NULL;
    // Проверка на существование файла - F_OK
    //if(access(request->fullPath, F_OK)==0){
    FILE* fp = fopen(request->fullPath, "wb+");
    if(request->body!=NULL && fp!=NULL && foundType){
        fwrite(request->body, 1, strlen(request->body), fp);
        response->headers[response->nHeadres].key = "Content-Length";
        char buf[20];
        int N = sprintf(buf, "%d", strlen("<h1>OK</h1>"))+1;
        response->headers[response->nHeadres].value = (char*) malloc (N);
        strcpy(response->headers[response->nHeadres].value, buf);
        response->nHeadres++;
        response->body = (char*) malloc (strlen("<h1>OK</h1>")+1);
        strcpy(response->body, "<h1>OK</h1>");
        response->code = 200;
        response->description = "OK";
        fclose(fp);
    }
    else{
        response->description = "BAD REQUEST";
        response->code = 400;
    }

    return 0;
}

int handle_delete_request(HTTP_request* request, HTTP_response* response){
    response->headers[response->nHeadres].key = "Content-Type";
    response->headers[response->nHeadres].value = "text/html";
    response->nHeadres++;
    response->body = NULL;

    if(access(request->fullPath, F_OK)==0){
        unlink(request->fullPath);
        response->headers[response->nHeadres].key = "Content-Length";
        char buf[20];
        int N = sprintf(buf, "%d", strlen("<h1>OK</h1>"))+1;
        response->headers[response->nHeadres].value = (char*) malloc (N);
        strcpy(response->headers[response->nHeadres].value, buf);
        response->nHeadres++;
        response->body = (char*) malloc (strlen("<h1>OK</h1>")+1);
        strcpy(response->body, "<h1>OK</h1>");
        response->code = 200;
        response->description = "OK";
    }
    else{
        response->description = "BAD REQUEST";
        response->code = 400;
    }

    return 0;
}

int handle_HTTP_request(char* req, char** res, char* rootDir){

    HTTP_request* request = parseRequest(req);
    HTTP_response* response = (HTTP_response*) malloc (sizeof(HTTP_response));
    response->protocol = "HTTP/1.0";
    response->headers = (HTTP_header*) malloc (50*sizeof(HTTP_header));
    response->nHeadres = 0;
    response->body = NULL;
    /*
     * Space for 50 headers, change to tree or class - i.e. realloc memory.
     * Enough for SPbCTF train. Actually, only two headers are set: Content-Type, Content-Length and Type
     * Thus, no need for extra space for headers - for now.
     */


    int pathMark = 0;
    int fpathMark = 0;
if(request!=NULL){
    if(request->path!=NULL && strlen(request->path)==1){
        char* path = (char*) malloc (strlen("index.html")+strlen(rootDir)+2);
        strcpy(path, rootDir);
        strcat(path, "/index.html");
        if(access(path, F_OK)==0){
            //free(request->path);
            request->path = (char*) malloc(sizeof("index.html")+1);
            pathMark = 1;
            strcpy(request->path, "/index.html");
        }
        free(path);
    }

    if(request->path!=NULL && strlen(request->path)!=1){
        request->fullPath = (char*) malloc (strlen(request->path)+strlen(rootDir)+1);
        fpathMark = 1;
        strcpy(request->fullPath, rootDir);
        strcat(request->fullPath, request->path);

        int result = 1;
        if((!strcmp(request->method, "GET"))||(!strcmp(request->method, "POST"))){
            result = handle_get_request(request, response);
        }
        else if(!strcmp(request->method, "SIZE")){
            result = handle_size_request(request, response);
        }
        else if(!strcmp(request->method, "PUT")){
            result = handle_put_request(request, response);
        }
        else if(!strcmp(request->method, "DELETE")){
            result = handle_delete_request(request, response);
        }
        if(result>0){
            response->code = 400;
            response->description = "BAD REQUEST";
        }
    }
    else{
        response->code = 400;
        response->description = "BAD REQUEST";
    }
}
else{
	response->code = 400;
        response->description = "BAD REQUEST";
}
    // Размер стоит подсчитать, для тестовой реализации - упрощенный вариант
    ssize_t hSize = 0;
    for(int j=0; j<response->nHeadres; j++){
        hSize = hSize + 4 + strlen(response->headers[j].key) + strlen(response->headers[j].value);
    }
    int bSize = 24+22;
    if(response->body!=NULL){
        if(strlen(response->body)>bSize){
            bSize = strlen(response->body);
        }
    }
    ssize_t resultSize = strlen(response->protocol) + 1 + 3 + 1 + strlen(response->description) + 2 + hSize + bSize+2+1;
    *res = (char*) malloc (resultSize);
    memset(*res, '\0', resultSize);
    char* cur = *res;
    sprintf(cur, "%s %d %s\r\n", response->protocol, response->code, response->description);
    cur += strlen(cur);
    for(int j=0; j<response->nHeadres; j++){
        sprintf(cur, "%s: %s\r\n", response->headers[j].key, response->headers[j].value);
        cur += strlen(cur);
        //free(response->headers[j].key);
        //free(response->headers[j].value);
    }

    // Вообще говоря, неверно - в файле могут находиться \0, так что копировать нужно все до конца файла побайтово
    if(response->body!=NULL && response->code==200){
        sprintf(cur, "\r\n");
        cur += strlen(cur);
        //printf("%s", response->body);
        snprintf(cur, bSize+1, "%s", response->body);
        cur += strlen(cur);
        free(response->body);
    }
    else if(response->code==400){
        sprintf(cur, "Content-Length: 20\r\n\r\n");
        cur += strlen(cur);
        sprintf(cur, "%s", "<h1>Bad request</h1>");
        cur += strlen(cur);
    }
    else{
        sprintf(cur, "Content-Length: 18\r\n\r\n");
        cur += strlen(cur);
        sprintf(cur, "<h1>NOT FOUND</h1>");
        cur += 1;
    }

    if(pathMark){
        free(request->path);
    }
    if(fpathMark){
        free(request->fullPath);
    }
    for(int j=0; j<response->nHeadres; j++){
        if(!strcmp(response->headers[j].key, "Content-Length")){
            free(response->headers[j].value);
        }
    }
    if(request!=NULL){
    free(request->headers);
    free(request);
}
    free(response->headers);
    free(response);
    return 0;
}
