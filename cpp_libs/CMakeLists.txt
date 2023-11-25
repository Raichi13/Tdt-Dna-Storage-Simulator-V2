cmake_minimum_required(VERSION 3.0)
project(TdTDnaStorageSimulator)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O2")

add_library(DnaTranscoder SHARED DnaTranscoder.cpp)
add_library(TdT SHARED TdT.cpp)

set_target_properties(DnaTranscoder PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/Build")
set_target_properties(TdT PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/Build")
