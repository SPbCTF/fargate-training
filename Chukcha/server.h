//
// Created by shtrikh17 on 21.01.18.
//

#ifndef SIMPLEHTTPSERVER_SERVER_H
#define SIMPLEHTTPSERVER_SERVER_H

#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <event2/listener.h>
#include <errno.h>
#include <unistd.h>
#include <pthread.h>


#include "commonOperations.h"

struct parameters{
    char* ip;
    int port;
    char* dir;
};

struct handlerInfo{
    evutil_socket_t fd;
    char* ip;
    int port;
    char* dir;
};

struct handlerCallbackArg{
    struct event* ev;
    char* ip;
    int port;
    char* dir;
};

void handler_cb(evutil_socket_t fd, short ev_flag, void* arg);
void* connection_handler(void* arg);
static void accept_conn_cb(struct evconnlistener* listener,
                           evutil_socket_t fd,
                           struct sockaddr* address,
                           int socklen,
                           void* ctx);
static void accept_error_cb(struct evconnlistener* listener,
                            evutil_socket_t fd,
                            struct sockaddr* address,
                            int socklen,
                            void* ctx);
int server(struct parameters* params);
#endif //SIMPLEHTTPSERVER_SERVER_H
