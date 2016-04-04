PROJECT(MyHello)
cmake_minimum_required(VERSION 3.0)
include(conanbuildinfo.cmake)
CONAN_BASIC_SETUP()

ADD_EXECUTABLE(main main.cpp)
ADD_EXECUTABLE(test_headers test_headers.cpp)
TARGET_LINK_LIBRARIES(main ${CONAN_LIBS})
TARGET_LINK_LIBRARIES(test_headers ${CONAN_LIBS})
