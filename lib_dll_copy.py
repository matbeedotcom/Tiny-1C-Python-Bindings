# -*- coding: utf-8 -*-
"""
Created on Wed Jul  8 09:06:20 2020

@author: dell
"""
import os, shutil

def copyfile(src_file, dst_path):  #将文件拷贝至dst_path目录下
    if not os.path.isfile(src_file):
        print("%s not exist!"%(src_file))
    else:
        if not os.path.exists(dst_path):
            os.makedirs(dst_path)                #创建路径
        shutil.copy(src_file,dst_path)      #复制文件
        print("copy %s -> %s"%( src_file,dst_path))


last_path=os.path.abspath(os.path.dirname(os.getcwd()))  #上级目录


x64_libirparse_dll=last_path+'\libirparse\Release\\x64\dll\libirparse.dll'
x64_libirprocess_dll=last_path+'\libirprocess\Release\\x64\dll\libirprocess.dll'
x64_libirtemp_dll=last_path+'\libirtemp\Release\\x64\dll\libirtemp.dll'
x64_libiruvc_dll=last_path+'\libiruvc\Release\\x64\dll\libiruvc.dll'
x64_src_dll_list=[x64_libirparse_dll,x64_libirprocess_dll,x64_libirtemp_dll,x64_libiruvc_dll]
x64_dst_dll_path='libir_sample\\x64\Debug'

x86_libirparse_dll=last_path+'\libirparse\Release\Win32\dll\libirparse.dll'
x86_libirprocess_dll=last_path+'\libirprocess\Release\Win32\dll\libirprocess.dll'
x86_libirtemp_dll=last_path+'\libirtemp\Release\Win32\dll\libirtemp.dll'
x86_libiruvc_dll=last_path+'\libiruvc\Release\Win32\dll\libiruvc.dll'
x86_src_dll_list=[x86_libirparse_dll,x86_libirprocess_dll,x86_libirtemp_dll,x86_libiruvc_dll]
x86_dst_dll_path='libir_sample\Win32\Debug'


x64_libirparse_lib=last_path+'\libirparse\Release\\x64\dll\libirparse.lib'
x64_libirprocess_lib=last_path+'\libirprocess\Release\\x64\dll\libirprocess.lib'
x64_libirtemp_lib=last_path+'\libirtemp\Release\\x64\dll\libirtemp.lib'
x64_libiruvc_lib=last_path+'\libiruvc\Release\\x64\dll\libiruvc.lib'
x64_src_lib_list=[x64_libirparse_lib,x64_libirprocess_lib,x64_libirtemp_lib,x64_libiruvc_lib]
x64_dst_lib_path=os.getcwd()+'\libs\\x64'

x86_libirparse_lib=last_path+'\libirparse\Release\Win32\dll\libirparse.lib'
x86_libirprocess_lib=last_path+'\libirprocess\Release\Win32\dll\libirprocess.lib'
x86_libirtemp_lib=last_path+'\libirtemp\Release\Win32\dll\libirtemp.lib'
x86_libiruvc_lib=last_path+'\libiruvc\Release\Win32\dll\libiruvc.lib'
x86_src_lib_list=[x86_libirparse_lib,x86_libirprocess_lib,x86_libirtemp_lib,x86_libiruvc_lib]
x86_dst_lib_path=os.getcwd()+'\libs\\x86'


libirparse_header=last_path+'\\libirparse\\include\\libirparse.h'
libirprocess_header=last_path+'\\libirprocess\\include\\libirprocess.h'
libirtemp_header=last_path+'\\libirtemp\\include\\libirtemp.h'
libiruvc_header=last_path+'\libiruvc\\include\\libiruvc.h'
thermal_camcmd_header=last_path+'\libiruvc\\include\\thermal_cam_cmd.h'
testcmd_header=last_path+'\libiruvc\\include\\test_cmd.h'
allconfig_header=last_path+'\libiruvc\\include\\all_config.h'

src_header_list=[libirparse_header, libirprocess_header, libirtemp_header,\
                 libiruvc_header, thermal_camcmd_header, testcmd_header,allconfig_header]
dst_header_path=os.getcwd()+'\include'


for i in range(len(x64_src_dll_list)):
    copyfile(x64_src_dll_list[i],x64_dst_dll_path)
    copyfile(x86_src_dll_list[i],x86_dst_dll_path)

for i in range(len(x64_src_lib_list)):
    copyfile(x64_src_lib_list[i],x64_dst_lib_path)
    copyfile(x86_src_lib_list[i],x86_dst_lib_path)
    
for i in range(len(src_header_list)):
    copyfile(src_header_list[i],dst_header_path)

input("copy completed!! Press any key to exit...")
    
