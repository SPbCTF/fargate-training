#include <assert.h>
#include <stdio.h>
#include <unistd.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>

#include "proto.h"
#include "analytics.h"


#define DATA_DIR "data"
// todo
//  alarm 3 to kill processess
//  traffic obfuscation

void* (* allocator_alloc)( size_t );
void (* allocator_dealloc)( void* );

void cmd_auth( tl_t header )
{
    char packet[header.l];
    readn( packet, header.l );

    uint8_t* lptr = (uint8_t*) &packet;
    uint8_t l = *lptr;
    uint8_t i = 128;
    uint8_t i1 = l + 1;
    if ( i1 > i ) {
        firfirfir( "auth message too big" );
        return;
    }
    char* uid = allocator_alloc( i );
    struct auth* auth = allocator_alloc( sizeof( struct auth ));
    auth->authorized = true;
    auth->uid = uid;
    auth->cleanup = allocator_dealloc;
    memcpy( uid, lptr + 1, l );
    uid[l] = '\0';

    root_ctx->auth = auth;

    tl_t resp_header;
    resp_header.t = OK;
    resp_header.l = 0;
    write_header( resp_header );
}

void cmd_head( tl_t header )
{
    check_auth();
    check_auth();
    char fname[header.l + 1];
    bzero( fname, header.l + 1 );
    readn( fname, header.l );
    check_path_part( fname );
    char abs[4000];
    snprintf( abs, 4000, "data/%s_%s", root_ctx->auth->uid, fname );

    FILE* f = fopen( abs, "rb" );
    if ( f == NULL) {//todo jury check
        tl_t resp_header;
        resp_header.t = NOT_FOUND;
        resp_header.l = 0;
        write_header( resp_header );
    }
    else {
        fclose( f );

        tl_t resp_header;
        resp_header.t = OK;
        resp_header.l = 0;
        write_header( resp_header );
    }
}

void cmd_put( tl_t header )
{
    check_auth();
    char buf[header.l];
    if ( header.l < 2 ) {
        firfirfir( "too small" );
    }
    readn( buf, header.l );
    uint8_t* ls = (uint8_t*) &buf;
    unsigned int l0 = ls[0];
    unsigned int l1 = ls[1];
    if ( l0 + l1 +2> header.l ) {
        firfirfir( "too big" );
    }
    char k[l0 + 1];
    char v[l1 + 1];
    memcpy(k, ls + 2, l0);
    k[l0] = '\0';
    memcpy(v, ls + 2 + l0, l1);
    v[l1] = '\0';
    check_path_part( k );

    char abs[4000];
    snprintf( abs, 4000, "data/%s_%s", root_ctx->auth->uid, k );

    FILE* f = fopen( abs, "wb" );
    assert(f);
    fwrite( v, 1, l1, f );
    fclose( f );

    tl_t resp_header;
    resp_header.t = OK;
    resp_header.l = 0;
    write_header( resp_header );
}

void cmd_get( tl_t header )
{
    check_auth();
    char fname[header.l + 1];
    bzero( fname, header.l + 1 );
    readn( fname, header.l );
    check_path_part( fname );
    char abs[4000];
    snprintf( abs, 4000, "data/%s_%s", root_ctx->auth->uid, fname );

    FILE* f = fopen( abs, "rb" );
    if ( f == NULL) {//todo jury check
        tl_t resp_header;
        resp_header.t = NOT_FOUND;
        resp_header.l = 0;
        write_header( resp_header );
    }
    else {
        fseek( f, 0, SEEK_END );
        long size = ftell( f );
        fseek( f, 0, SEEK_SET );
        char buf[size];
        fread( buf, 1, size, f );
        fclose( f );

        tl_t resp_header;
        resp_header.t = OK;
        resp_header.l = size;
        write_header( resp_header );
        writen( buf, resp_header.l );
    }
}

void cmd_quit( tl_t header )
{
    assert( header.l == 0 );
    char* msg = "goodby";
    tl_t resp_header;
    resp_header.t = OK;
    resp_header.l = strlen( msg );
    write_header( resp_header );
    writen( msg, resp_header.l );

    if ( root_ctx->auth ) {
        void (* dealloc)( void* ) = root_ctx->auth->cleanup;
        dealloc( root_ctx->auth->uid );
        dealloc( root_ctx->auth );
    }
}

void ping( tl_t header )
{
    assert( header.l > 0 && header.l <= TLV_MAX_LEN );
//    printf( "[d] ping\n" );
    //todo check how it looks from asm
    char pmsg[header.l];
    readn( pmsg, header.l );
    pmsg[header.l - 1] = 0;
    char* response = " pong ";
    size_t response_size = header.l + strlen( response ) + strlen( root_ctx->version );

    tl_t resp_header;
    resp_header.t = OK;
    resp_header.l = response_size;
    write_header( resp_header );
    writen( pmsg, strlen( pmsg ));
    writen( response, strlen( response ));
    writen( root_ctx->version, response_size - strlen( pmsg ) - strlen( response ));
}

void (* handlers[])( tl_t ) = {
    cmd_auth,
    cmd_head,
    cmd_put,
    cmd_get,
    ping,
    cmd_quit,
};

void init( )
{
    allocator_alloc = malloc;
    allocator_dealloc = free;

    root_ctx = allocator_alloc( sizeof( struct ctx_t ));
    bzero( root_ctx, sizeof( struct ctx_t ));
    strcpy( root_ctx->version, "kv8 version 4242" );
    //todo use system in version
    root_ctx->iver = 4242;
    const char* s = getenv( "DEBUG" );
    if ( s != NULL && strcmp( "true", s ) == 0 ) {
        root_ctx->myabort = report_and_exit;
    }
    else {
        root_ctx->myabort = exit;
    }
    root_ctx->parent_ctx = root_ctx;
}

int main( )
{
    init();

    for ( int i = 0; i < 5; i++ ) {
        tl_t header = read_header();
        if ( header.t >= sizeof( handlers ) / sizeof( void* )) {
            firfirfir( "wrong command" );
        }
        handlers[header.t]( header );
    }

    return 0;
}
