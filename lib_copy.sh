#! /bin/sh

cp ../libirtemp/include/libirtemp.h  ./include
cp ../libirprocess/include/libirprocess.h  ./include
cp ../libirparse/include/libirparse.h  ./include
cp ../libiruvc/include/libiruvc.h  ./include
cp ../libiruvc/include/all_config.h  ./include
cp ../libiruvc/include/thermal_cam_cmd.h  ./include
echo "header file copy to /include directory finished !!!"

cp ../libirtemp/build/libirtemp.so  ./libs
cp ../libirprocess/build/libirprocess.so  ./libs
cp ../libirparse/build/libirparse.so  ./libs
cp ../libiruvc/build/libiruvc.so*  ./libs
echo "lib copy to ./libs directory finished !!!"
