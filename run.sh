#!/bin/bash

echo "=== Linux OJ 评测核心启动脚本 ==="

# 检查是否在Linux系统上
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "错误: 此脚本需要在Linux系统上运行"
    exit 1
fi

# 检查必要的依赖
echo "检查系统依赖..."

# 检查g++
if ! command -v g++ &> /dev/null; then
    echo "错误: 未找到g++编译器，请安装g++"
    exit 1
fi

# 检查jsoncpp
if ! pkg-config --exists jsoncpp; then
    echo "错误: 未找到jsoncpp库，请安装libjsoncpp-dev"
    echo "Ubuntu/Debian: sudo apt-get install libjsoncpp-dev"
    echo "CentOS/RHEL: sudo yum install jsoncpp-devel"
    exit 1
fi

# 检查seccomp
if ! pkg-config --exists libseccomp; then
    echo "错误: 未找到libseccomp库，请安装libseccomp-dev"
    echo "Ubuntu/Debian: sudo apt-get install libseccomp-dev"
    echo "CentOS/RHEL: sudo yum install libseccomp-devel"
    exit 1
fi

echo "系统依赖检查完成"

# 创建必要的目录
echo "创建目录结构..."
mkdir -p stdin stdout

# 编译测试程序
echo "编译测试程序..."
g++ -o test test.cpp -std=c++11
if [ $? -ne 0 ]; then
    echo "错误: 编译测试程序失败"
    exit 1
fi

# 编译评测核心
echo "编译评测核心..."
g++ -o judge_core judge_core.cpp -std=c++17 \
    $(pkg-config --cflags --libs jsoncpp) \
    $(pkg-config --cflags --libs libseccomp) \
    -lstdc++fs
if [ $? -ne 0 ]; then
    echo "错误: 编译评测核心失败"
    exit 1
fi

# 设置执行权限
chmod +x judge_core
chmod +x test

echo "编译完成"

# 运行评测
echo "开始评测..."
./judge_core

if [ $? -eq 0 ]; then
    echo "评测完成！"
    echo "查看结果: cat execute_message.json"
else
    echo "评测过程中出现错误"
    exit 1
fi 