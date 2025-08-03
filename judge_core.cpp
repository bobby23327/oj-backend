#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <sys/wait.h>
#include <sys/resource.h>
#include <sys/time.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>
#include <fcntl.h>
#include <signal.h>
#include <seccomp.h>
#include <jsoncpp/json/json.h>
#include <cstring>
#include <filesystem>

namespace fs = std::filesystem;

struct JudgeResult {
    int status;
    int time_used;
    int memory_used;
    std::string error_message;
    std::string output;
    bool time_limit_exceeded;
    bool memory_limit_exceeded;
    bool runtime_error;
    bool system_error;
};

class JudgeCore {
private:
    Json::Value limits;
    std::string work_dir;
    std::string sandbox_dir;
    
public:
    JudgeCore(const std::string& limits_file) {
        loadLimits(limits_file);
        work_dir = fs::current_path().string();
        sandbox_dir = work_dir + "/sandbox";
        setupSandbox();
    }
    
    ~JudgeCore() {
        cleanupSandbox();
    }
    
    void loadLimits(const std::string& limits_file) {
        std::ifstream file(limits_file);
        if (!file.is_open()) {
            throw std::runtime_error("无法打开限制文件: " + limits_file);
        }
        
        Json::CharReaderBuilder builder;
        Json::Value root;
        std::string errors;
        
        if (!Json::parseFromStream(builder, file, &root, &errors)) {
            throw std::runtime_error("JSON解析错误: " + errors);
        }
        
        limits = root;
    }
    
    void setupSandbox() {
        // 创建沙箱目录
        fs::create_directories(sandbox_dir);
        fs::create_directories(sandbox_dir + "/bin");
        fs::create_directories(sandbox_dir + "/lib");
        fs::create_directories(sandbox_dir + "/lib64");
        fs::create_directories(sandbox_dir + "/usr");
        fs::create_directories(sandbox_dir + "/tmp");
        
        // 复制必要的系统文件到沙箱
        system(("cp /bin/bash " + sandbox_dir + "/bin/").c_str());
        system(("cp -r /lib/* " + sandbox_dir + "/lib/ 2>/dev/null || true").c_str());
        system(("cp -r /lib64/* " + sandbox_dir + "/lib64/ 2>/dev/null || true").c_str());
        system(("cp -r /usr/lib/* " + sandbox_dir + "/usr/lib/ 2>/dev/null || true").c_str());
    }
    
    void cleanupSandbox() {
        fs::remove_all(sandbox_dir);
    }
    
    JudgeResult executeProgram(const std::string& program_path, 
                             const std::string& input_file,
                             const std::string& output_file) {
        JudgeResult result = {};
        
        // 复制程序到沙箱
        std::string sandbox_program = sandbox_dir + "/program";
        fs::copy_file(program_path, sandbox_program, fs::copy_options::overwrite_existing);
        
        // 复制输入文件到沙箱
        std::string sandbox_input = sandbox_dir + "/input";
        fs::copy_file(input_file, sandbox_input, fs::copy_options::overwrite_existing);
        
        // 设置输出文件路径
        std::string sandbox_output = sandbox_dir + "/output";
        
        // 创建管道用于监控
        int pipe_fd[2];
        if (pipe(pipe_fd) == -1) {
            result.system_error = true;
            result.error_message = "创建管道失败";
            return result;
        }
        
        pid_t pid = fork();
        if (pid == -1) {
            result.system_error = true;
            result.error_message = "fork失败";
            return result;
        }
        
        if (pid == 0) {
            // 子进程 - 在沙箱中执行程序
            setupChildProcess(sandbox_program, sandbox_input, sandbox_output, pipe_fd);
            exit(1);
        } else {
            // 父进程 - 监控子进程
            return monitorChildProcess(pid, pipe_fd, output_file, result);
        }
    }
    
private:
    void setupChildProcess(const std::string& program, 
                          const std::string& input, 
                          const std::string& output,
                          int pipe_fd[2]) {
        // 关闭父进程端的管道
        close(pipe_fd[0]);
        
        // 重定向输入输出
        int input_fd = open(input.c_str(), O_RDONLY);
        int output_fd = open(output.c_str(), O_WRONLY | O_CREAT | O_TRUNC, 0644);
        
        if (input_fd == -1 || output_fd == -1) {
            write(pipe_fd[1], "文件重定向失败", 20);
            exit(1);
        }
        
        dup2(input_fd, STDIN_FILENO);
        dup2(output_fd, STDOUT_FILENO);
        dup2(output_fd, STDERR_FILENO);
        
        close(input_fd);
        close(output_fd);
        close(pipe_fd[1]);
        
        // 设置资源限制
        struct rlimit rlim;
        
        // 时间限制
        rlim.rlim_cur = limits["time_limit"].asInt() / 1000;
        rlim.rlim_max = limits["time_limit"].asInt() / 1000;
        setrlimit(RLIMIT_CPU, &rlim);
        
        // 内存限制
        rlim.rlim_cur = limits["memory_limit"].asInt() * 1024;
        rlim.rlim_max = limits["memory_limit"].asInt() * 1024;
        setrlimit(RLIMIT_AS, &rlim);
        
        // 输出大小限制
        rlim.rlim_cur = limits["output_limit"].asInt();
        rlim.rlim_max = limits["output_limit"].asInt();
        setrlimit(RLIMIT_FSIZE, &rlim);
        
        // 进程数限制
        rlim.rlim_cur = limits["process_limit"].asInt();
        rlim.rlim_max = limits["process_limit"].asInt();
        setrlimit(RLIMIT_NPROC, &rlim);
        
        // 栈大小限制
        rlim.rlim_cur = limits["stack_limit"].asInt() * 1024;
        rlim.rlim_max = limits["stack_limit"].asInt() * 1024;
        setrlimit(RLIMIT_STACK, &rlim);
        
        // 设置seccomp过滤器
        if (limits["seccomp_enabled"].asBool()) {
            setupSeccomp();
        }
        
        // chroot到沙箱目录
        if (limits["chroot_enabled"].asBool()) {
            if (chroot(sandbox_dir.c_str()) == -1) {
                write(pipe_fd[1], "chroot失败", 15);
                exit(1);
            }
            chdir("/");
        }
        
        // 执行程序
        execl(program.c_str(), program.c_str(), nullptr);
        
        // 如果execl失败
        write(pipe_fd[1], "程序执行失败", 20);
        exit(1);
    }
    
    void setupSeccomp() {
        scmp_filter_ctx ctx = seccomp_init(SCMP_ACT_KILL);
        if (ctx == nullptr) return;
        
        // 允许基本系统调用
        seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(read), 0);
        seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(write), 0);
        seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(open), 0);
        seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(close), 0);
        seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(fstat), 0);
        seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(mmap), 0);
        seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(mprotect), 0);
        seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(munmap), 0);
        seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(brk), 0);
        seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(rt_sigaction), 0);
        seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(rt_sigprocmask), 0);
        seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(rt_sigreturn), 0);
        seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(ioctl), 0);
        seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(access), 0);
        seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(exit_group), 0);
        seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(exit), 0);
        
        seccomp_load(ctx);
        seccomp_release(ctx);
    }
    
    JudgeResult monitorChildProcess(pid_t pid, int pipe_fd[2], 
                                  const std::string& output_file,
                                  JudgeResult& result) {
        close(pipe_fd[1]);
        
        struct timeval start_time, end_time;
        gettimeofday(&start_time, nullptr);
        
        int status;
        struct rusage usage;
        
        // 等待子进程结束
        wait4(pid, &status, 0, &usage);
        
        gettimeofday(&end_time, nullptr);
        
        // 计算时间使用量（毫秒）
        result.time_used = (end_time.tv_sec - start_time.tv_sec) * 1000 + 
                          (end_time.tv_usec - start_time.tv_usec) / 1000;
        
        // 计算内存使用量（KB）
        result.memory_used = usage.ru_maxrss;
        
        // 检查执行结果
        if (WIFEXITED(status)) {
            result.status = WEXITSTATUS(status);
            if (result.status != 0) {
                result.runtime_error = true;
                result.error_message = "程序异常退出，退出码: " + std::to_string(result.status);
            }
        } else if (WIFSIGNALED(status)) {
            int signal = WTERMSIG(status);
            result.status = signal;
            
            if (signal == SIGXCPU) {
                result.time_limit_exceeded = true;
                result.error_message = "时间限制超时";
            } else if (signal == SIGXFSZ) {
                result.error_message = "输出文件大小超限";
            } else if (signal == SIGSEGV) {
                result.runtime_error = true;
                result.error_message = "段错误";
            } else if (signal == SIGABRT) {
                result.runtime_error = true;
                result.error_message = "程序异常终止";
            } else {
                result.runtime_error = true;
                result.error_message = "程序被信号终止: " + std::to_string(signal);
            }
        }
        
        // 检查时间限制
        if (result.time_used > limits["time_limit"].asInt()) {
            result.time_limit_exceeded = true;
            result.error_message = "时间限制超时";
        }
        
        // 检查内存限制
        if (result.memory_used > limits["memory_limit"].asInt()) {
            result.memory_limit_exceeded = true;
            result.error_message = "内存限制超限";
        }
        
        // 读取错误信息
        char buffer[1024];
        ssize_t bytes_read = read(pipe_fd[0], buffer, sizeof(buffer) - 1);
        if (bytes_read > 0) {
            buffer[bytes_read] = '\0';
            result.error_message = std::string(buffer);
        }
        
        close(pipe_fd[0]);
        
        // 复制输出文件
        std::string sandbox_output = sandbox_dir + "/output";
        if (fs::exists(sandbox_output)) {
            fs::copy_file(sandbox_output, output_file, fs::copy_options::overwrite_existing);
            
            // 读取输出内容
            std::ifstream output_stream(output_file);
            if (output_stream.is_open()) {
                result.output = std::string(std::istreambuf_iterator<char>(output_stream),
                                          std::istreambuf_iterator<char>());
                output_stream.close();
            }
        }
        
        return result;
    }
};

int main() {
    try {
        JudgeCore judge("limits.json");
        
        // 获取所有输入文件
        std::vector<std::string> input_files;
        for (const auto& entry : fs::directory_iterator("stdin")) {
            if (entry.path().extension() == ".in") {
                input_files.push_back(entry.path().string());
            }
        }
        
        // 执行所有测试用例
        Json::Value results;
        results["test_cases"] = Json::Value(Json::arrayValue);
        
        for (const auto& input_file : input_files) {
            std::string test_name = fs::path(input_file).stem().string();
            std::string output_file = "stdout/" + test_name + ".out";
            
            JudgeResult result = judge.executeProgram("./test", input_file, output_file);
            
            Json::Value test_result;
            test_result["test_name"] = test_name;
            test_result["status"] = result.status;
            test_result["time_used"] = result.time_used;
            test_result["memory_used"] = result.memory_used;
            test_result["error_message"] = result.error_message;
            test_result["output"] = result.output;
            test_result["time_limit_exceeded"] = result.time_limit_exceeded;
            test_result["memory_limit_exceeded"] = result.memory_limit_exceeded;
            test_result["runtime_error"] = result.runtime_error;
            test_result["system_error"] = result.system_error;
            
            results["test_cases"].append(test_result);
        }
        
        // 保存执行结果
        std::ofstream result_file("execute_message.json");
        Json::StyledWriter writer;
        result_file << writer.write(results);
        result_file.close();
        
        std::cout << "评测完成，结果已保存到 execute_message.json" << std::endl;
        
    } catch (const std::exception& e) {
        std::cerr << "错误: " << e.what() << std::endl;
        return 1;
    }
    
    return 0;
} 