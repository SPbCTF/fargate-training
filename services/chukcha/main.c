#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

#include <pthread.h>

#include "myHTTP.h"
#include "commonOperations.h"
#include "server.h"

extern int opterr;
extern char* optarg;

int parse_argv(int argc, char** argv, struct parameters* params){

    int opt = 0;
    opterr = 0;
    while((opt=getopt(argc, argv, "h:p:d:"))!=-1){
        switch(opt){
            case 'h':
                params->ip = (char*) malloc (strlen(optarg)+1);
                strcpy(params->ip, optarg);
                break;
            case 'p':
                params->port = atoi(optarg);
                break;
            case 'd':
                params->dir = (char*) malloc (strlen(optarg)+1);
                strcpy(params->dir, optarg);
                break;
            default:
                break;
        }
    }

    if(params->ip==NULL || params->port==0 || params->dir==NULL)
        return -1;

    return 0;
}

void daemonize(void){
    pid_t pid = fork();
    if(pid<0){
        perror("daemonize.fork error");
        exit(1);
    }
    if(pid>0){
        char log[100];
        snprintf(log, 100, "New pid: %d\n", pid);
        printLog(log);
        exit(0);
    }
    if(setsid()==-1){
        perror("daemonize.setsid error");
        exit(1);
    }
    close(STDOUT_FILENO);
    close(STDIN_FILENO);
    close(STDOUT_FILENO);
}

int main(int argc, char** argv){

    printLog("==================================");

    struct parameters params = {NULL, 0, NULL};
    if(parse_argv(argc, argv, &params)!=0){
        perror("Wrong command line arguments.\n");
        exit(1);
    }
    printLog("Successful parsing");
    char log[1024];
    snprintf(log, 1024, "ip: %s\nport: %d\ndir: %s\n", params.ip, params.port, params.dir);
    printLog(log);

    //daemonize();

    server(&params);

    /*char str[] = "GET /index.txt HTTP/1.0\r\nHost: www.shtrikh17.com\r\nCookie: abcd\r\n\r\naaa";
    char* buf;
    handle_HTTP_request(str, &buf, "/home/shtrikh17");
    printf("%s", buf);*/
    return 0;
}
