cmake_minimum_required(VERSION 3.0)
project(DnaTranscoder)

set(CMAKE_CXX_STANDARD 11)

add_library(DnaTranscoder SHARED DnaTranscoder.cpp)

set_target_properties(DnaTranscoder PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/Build")
