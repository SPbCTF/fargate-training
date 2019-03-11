cmake_minimum_required(VERSION 3.0)
project(kv8)

#find_package(OpenSSL)
#include_directories(${OPENSSL_INCLUDE_DIR})

add_executable(kv8 main.c proto.c analytics.c)
#target_link_libraries(kv8 crypto)
