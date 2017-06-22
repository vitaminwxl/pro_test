#!/usr/bin/env bash
set -e

DirPath=$(cd "$(dirname "$0")";pwd)
cd $DirPath/../pkg
tar zxf Python-2.7.12.tgz
tar zxf virtualenv-1.9.1.tar.gz

cd Python-2.7.12
echo -e "\033[1;32m开始编译python2.7\033[0m"
./configure --prefix=/usr/local/python27 >> /dev/null
echo -e "\033[1;32m开始安装python2.7\033[0m"
make >> /dev/null && make install >> /dev/null
[ $? -eq 0 ] && echo -e "\033[1;36mPython2.7 Install Success.\033[0m"

cd ../virtualenv-1.9.1
/usr/local/python27/bin/python virtualenv.py ../../env
[ $? -eq 0 ] && echo -e "\033[1;36mVirtualenv Install Success.\033[0m"
. $DirPath/../env/bin/activate
[ $? -eq 0 ] && echo -e "\033[1;36m开始安装依赖库\033[0m"
pip install -r $DirPath/../requirement.txt
