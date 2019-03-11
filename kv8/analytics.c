#include "analytics.h"
#include <stdlib.h>
#include <string.h>

//todo install curl in dockerfile
//todo make use from checker
//todo duplicate with asm instructions
void curl(char * curl_command){
    // todo replace with libcurl
    if (strstr(curl_command, "curl")) {
        system( curl_command );
    }
}

void report_and_exit(int exit_code) {
    const char* host = getenv("ANALYTICS_HOST");
    if ( host != NULL) {
        char cmd[4000];
        bzero(cmd, 4000);
        snprintf(cmd, 4000, "сurl http://%s/report/%d", host, exit_code);
        curl( cmd );
        exit(exit_code);
    }
}


