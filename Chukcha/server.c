//
// Created by shtrikh17 on 21.01.18.
//

#include "server.h"
#include "myHTTP.h"

void handler_cb(evutil_socket_t fd, short ev_flag, void* arg){
    /*
     * IMPORTANT: Persistent HTTP connections are not supported yet. Connection closed after successful response.
     */
    struct handlerCallbackArg* hArg = (struct handlerCallbackArg*)arg;

    char log[255];
    snprintf(log, 255, "Incoming request from [%s:%d]", hArg->ip, hArg->port);
    printLog(log);

    char* request = (char*) malloc(1024*sizeof(char));              // The server is simple :) Thus only up to 1024 bytes
    int RecvSize = recv(fd, request, 1024, MSG_NOSIGNAL);
    if(RecvSize==0 && errno!=EAGAIN){

        struct event_base* base = event_get_base(hArg->ev);

        event_free(hArg->ev);
        shutdown(fd, SHUT_RDWR);
        close(fd);
        free(hArg);
        event_base_loopbreak(base);
        //event_base_free(base);
    }
    else if(RecvSize!=0){

        printLog("REQUEST:");
        printLog(request);
        //send(fd, Buffer, RecvSize, MSG_NOSIGNAL);
        char* response;
        handle_HTTP_request(request, &response, hArg->dir);
        int l = strlen(response);

        printLog("RESPONSE:");
        printLog(response);
        //printf(response);
        //printf("%d", l);
        send(fd, response, l, MSG_NOSIGNAL);
        free(request);
        free(response);
        free(hArg->ip);
        //event_free(hArg->ev);
        shutdown(fd, SHUT_RDWR);
        close(fd);
        //free(hArg);

        //struct event_base* base = event_get_base(hArg->ev);
        //event_base_loopbreak(base);
    }
}

void* connection_handler(void* arg){

    struct handlerInfo* hInfo = (struct handlerInfo*)arg;

    struct event_base* base = event_base_new();

    struct event* ev;
    struct handlerCallbackArg* hArg = (struct handlerCallbackArg*) malloc (sizeof(struct handlerCallbackArg));

    ev = event_new(base, hInfo->fd, (EV_READ | EV_PERSIST), handler_cb, hArg);

    hArg->ev = ev;
    hArg->ip = hInfo->ip;
    hArg->port = hInfo->port;
    hArg->dir = hInfo->dir;

    free(arg);
    /*char log[100];
    snprintf(log, 100, "ev: %X", ev);
    printLog(log);*/

    event_add(ev, NULL);
    event_base_dispatch(base);
    event_base_free(base);

    //pthread_exit(0);
}

static void accept_conn_cb(struct evconnlistener* listener,
                           evutil_socket_t fd,
                           struct sockaddr* address,
                           int socklen,
                           void* arg){

    printLog("--------\nAccepting incoming connection from:");
    int res;

    // Получим соответствующий base для event_base
    struct event_base* base = evconnlistener_get_base(listener);
    struct parameters* params = (struct parameters*) arg;

    char* ip = (char*) malloc (255*sizeof(char));
    struct sockaddr_in* sa = (struct sockaddr_in*)address;
    res = inet_ntop(AF_INET, &sa->sin_addr, ip, 255);

    if(!res){
        printLog("Conversion error\n");
        exit(1);
    }

    char buf[1024];
    snprintf(buf, 1024, "ip: %s\nport: %d\n--------", ip, sa->sin_port);
    printLog(buf);

    pthread_t thread;
    struct handlerInfo* hInfo = (struct handlerInfo*) malloc (sizeof(struct handlerInfo));
    hInfo->fd = fd;
    hInfo->ip = ip;
    hInfo->port = sa->sin_port;
    hInfo->dir = params->dir;


    res = pthread_create(&thread, NULL, connection_handler, hInfo);
    if(res!=0){
        printLog("Thread creation error\n");
        exit(1);
    }
    pthread_detach(thread);

}

static void accept_error_cb(struct evconnlistener* listener,
                            evutil_socket_t fd,
                            struct sockaddr* address,
                            int socklen,
                            void* ctx){
    printLog("Incoming connection error\n");
    // Получим соответствующий base для event_base
    struct event_base* base = evconnlistener_get_base(listener);

    // Получим код ошибки
    int err = EVUTIL_SOCKET_ERROR();

    // Отправляем сообщение об ошибке в лог
    char buf[1024];
    snprintf(buf, 1024, "Error = %d \"%s\"\n", err, evutil_socket_error_to_string(err));
    printLog(buf);

    // Выходим из цикла обработки сообщений
    event_base_loopexit(base, NULL);
}


int server(struct parameters* params){
    // Создадим сокет

    int MasterSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);

    struct sockaddr_in sin;
    sin.sin_family = AF_INET;
    sin.sin_port = htons(params->port);
    int t = inet_pton(AF_INET, params->ip, &(sin.sin_addr));
    if(t==0){
        printLog("inet_pton address failure\n");
        exit(1);
    }
    else if(t==-1){
        printLog("inet_pton common failure\n");
        exit(1);
    }

    if(bind(MasterSocket, &sin, sizeof(sin))<0){
        printLog("Bind failure\n");
        exit(1);
    }

    if(listen(MasterSocket, SOMAXCONN)<0){
        printLog("Listen failure\n");
        exit(1);
    }

    // Создадим структуру для цикла обработки событий
    struct event_base* base = event_base_new();

    // Создадим listener
    struct evconnlistener* listener = evconnlistener_new(base,
                                                         accept_conn_cb,
                                                         params,
                                                         LEV_OPT_CLOSE_ON_FREE | LEV_OPT_REUSEABLE,
                                                         0,
                                                         MasterSocket);
    evconnlistener_set_error_cb(listener, accept_error_cb);

    printLog("Starting event_base\n");

    // Запустим цикл обработки событий
    event_base_dispatch(base);
    event_base_free(base);

    printLog("Server exit\n");
    return 0;
}
