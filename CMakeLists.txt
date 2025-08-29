cmake_minimum_required(VERSION 3.1)
project(sample
  LANGUAGES CXX
)
include(extern_lib.cmake)
set(SRC_LIST
	camera.cpp
	cmd.cpp
	data.cpp
	display.cpp
	sample.cpp	
	temperature.cpp
)
include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)


link_directories(${CMAKE_CURRENT_SOURCE_DIR}/libs)

add_executable(sample ${SRC_LIST})
target_link_libraries(sample
    iruvc
    irtemp
    irprocess
    irparse
    pthread
    usb-1.0
    -lm
#opencv related
    opencv_highgui
    opencv_imgcodecs
    opencv_imgproc 
    opencv_core
)
