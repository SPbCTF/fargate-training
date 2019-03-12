
#include "proto.h"


void firfirfir( const char *msg) {
    perror( msg );
    void (* myabort)( int ) = root_ctx->myabort;
    myabort( 1337 / 4242 );

    
}



void writen(void *buf, size_t n) {
    assert( n > 0 );
    assert( buf != NULL );
    size_t bytes_written = 0;
    void *it=buf;
    while (1) {
        assert( bytes_written < n );
        ssize_t res = write(STDOUT_FILENO, it, n - bytes_written);
        if (res < 0) {
            firfirfir( "reading error" );
        } else if (res == 0) {
            firfirfir( "reading eof" );
        } else {
            it += res;
            bytes_written += res;
            if ( n == bytes_written ) {
                break;
            }
        }
    }
}

void readn(void *buf, size_t n) {
    assert( n > 0 );
    assert( buf != NULL );
    size_t bytes_read = 0;
    void *it=buf;
    while (1) {
        assert( bytes_read < n );
        ssize_t res = read(STDIN_FILENO, it, n - bytes_read);
        if (res < 0) {
            firfirfir( "reading error" );
        } else if (res == 0) {
            // firfirfir( "reading eof" );
            exit(0);
        } else {
            it += res;
            bytes_read += res;
            if ( n == bytes_read ) {
                break;
            }
        }
    }
}

tl_t read_header() {
    static_assert( sizeof( tl_t ) == 16, "tl is 128 bit" );
    tl_t h = {0, 0};
    readn( &h, sizeof(tl_t));
    if (h.l > TLV_MAX_LEN) {
        firfirfir( "msg too big" );
    }
    return h;
}

void write_header(tl_t header) {
    writen(&header, sizeof(header));
}

void check_auth(){
    if ( !root_ctx->auth ) {
        firfirfir( "not authorized" );
    }
    check_path_part( root_ctx->auth->uid );
}
void check_path_part( const char* s )
{
    size_t l = strlen( s );
    if ( l == 0 || l > 128 ) {
        firfirfir( "strange uid" );
    }
    for ( int i = 0; i < l; i++ ) {
        char c = s[i];
        if ( c >= 'a' && c <= 'z' ) {
            continue;
        } else if ( c >= 'A' && c <= 'Z' ) {
            continue;
        } else if ( c >= '0' && c <= '9' ) {
            continue;
        } else {
            firfirfir( "bad uid" );
        }
    }
}
