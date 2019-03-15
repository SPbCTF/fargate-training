cmake_minimum_required(VERSION 2.0)
project(final C)

set(CMAKE_C_STANDARD 99)
set(CMAKE_C_FLAGS "-std=c99")
add_executable(final main.c myHTTP.c myHTTP.h commonOperations.c commonOperations.h server.c server.h)
target_link_libraries(final event)
target_link_libraries(final pthread)
set_target_properties(final PROPERTIES COMPILE_FLAGS "-m32 -fno-stack-protector -z execstack -no-pie" LINK_FLAGS "-m32 -fno-stack-protector -z execstack -no-pie")
