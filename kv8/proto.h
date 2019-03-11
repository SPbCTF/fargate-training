#pragma once

#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdlib.h>
#include <stdio.h>
#include <assert.h>
#include <stdio.h>
#include <stdbool.h>

#define TLV_MAX_LEN 1024
#define CMD_PING 0
#define OK 200
#define NOT_FOUND 404

struct tl
{
    uint64_t t;
    uint64_t l;
};

typedef struct tl tl_t;

struct ctx_t
{
    char version[32];
    uint32_t iver;
    struct auth* auth;
    void* myabort;
    struct ctx_t *parent_ctx;// loops to this for root
};

struct ctx_t* root_ctx;


struct auth
{
    bool authorized;
    char* uid;
    void* cleanup;
    char padding[256];
};

void firfirfir( const char* msg );
void writen( void* buf, size_t n );
void readn( void* buf, size_t n );
tl_t read_header( );
void write_header( tl_t header );
void check_auth();
void check_path_part( const char* s );
