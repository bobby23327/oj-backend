# Linux OJ 评测核心

一个简单但功能完整的Linux在线评测系统核心，提供安全的沙箱执行环境。

## 功能特性

- 🔒 **安全沙箱**: 使用chroot和seccomp提供进程隔离
- ⏱️ **资源限制**: 时间、内存、输出大小等多维度限制
- 📊 **详细监控**: 实时监控程序执行状态和资源使用
- 🎯 **精确评测**: 支持多测试用例批量评测
- 📝 **JSON输出**: 结构化的评测结果输出

## 系统要求

- Linux操作系统
- g++编译器 (支持C++17)
- libjsoncpp-dev
- libseccomp-dev

## 安装依赖

### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install g++ libjsoncpp-dev libseccomp-dev
```

### CentOS/RHEL
```bash
sudo yum install gcc-c++ jsoncpp-devel libseccomp-devel
```

## 文件结构

```
judge_core/
├── limits.json          # 执行限制配置
├── stdin/              # 输入测试用例
│   ├── aplusb1.in
│   ├── aplusb2.in
│   └── aplusb3.in
├── stdout/             # 期望输出文件
│   ├── aplusb1.out
│   ├── aplusb2.out
│   └── aplusb3.out
├── test.cpp            # 待评测程序
├── judge_core.cpp      # 评测核心
├── run.sh              # 一键启动脚本
└── README.md           # 说明文档
```

## 使用方法

### 一键启动
```bash
chmod +x run.sh
./run.sh
```

### 手动编译运行
```bash
# 编译测试程序
g++ -o test test.cpp -std=c++11

# 编译评测核心
g++ -o judge_core judge_core.cpp -std=c++17 \
    $(pkg-config --cflags --libs jsoncpp) \
    $(pkg-config --cflags --libs libseccomp) \
    -lstdc++fs

# 运行评测
./judge_core
```

## 配置说明

### limits.json 配置项

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| time_limit | 时间限制(毫秒) | 1000 |
| memory_limit | 内存限制(KB) | 65536 |
| cpu_limit | CPU核心数限制 | 1 |
| output_limit | 输出大小限制(字节) | 65536 |
| stack_limit | 栈大小限制(KB) | 8192 |
| process_limit | 进程数限制 | 1 |
| file_size_limit | 文件大小限制(字节) | 1048576 |
| network_enabled | 是否允许网络 | false |
| chroot_enabled | 是否启用chroot | true |
| seccomp_enabled | 是否启用seccomp | true |

## 输出结果

评测完成后会生成 `execute_message.json` 文件，包含详细的评测结果：

```json
{
  "test_cases": [
    {
      "test_name": "aplusb1",
      "status": 0,
      "time_used": 5,
      "memory_used": 1024,
      "error_message": "",
      "output": "3\n",
      "time_limit_exceeded": false,
      "memory_limit_exceeded": false,
      "runtime_error": false,
      "system_error": false
    }
  ]
}
```

## 安全特性

1. **进程隔离**: 使用fork创建独立进程
2. **文件系统隔离**: chroot限制文件系统访问
3. **系统调用过滤**: seccomp限制系统调用
4. **资源限制**: 多维度资源使用限制
5. **沙箱环境**: 独立的执行环境

## 错误处理

系统能够检测和处理以下错误：

- 时间限制超时 (SIGXCPU)
- 内存限制超限
- 输出文件大小超限 (SIGXFSZ)
- 段错误 (SIGSEGV)
- 程序异常终止 (SIGABRT)
- 系统调用违规 (seccomp)

## 扩展使用

### 添加新的测试用例

1. 在 `stdin/` 目录添加 `.in` 文件
2. 在 `stdout/` 目录添加对应的 `.out` 文件
3. 重新运行评测

### 修改待评测程序

编辑 `test.cpp` 文件，然后重新编译运行。

### 调整执行限制

修改 `limits.json` 文件中的配置项。

## 注意事项

1. 需要在Linux系统上运行
2. 需要root权限或适当的系统权限
3. 确保系统已安装必要的依赖库
4. 评测程序应该是可执行文件

## 许可证

本项目采用MIT许可证。 