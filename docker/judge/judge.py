"""
评测服务主程序
"""
import os
import json
import time
import subprocess
import docker
from typing import Dict, Any
import redis
from datetime import datetime

# 配置
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
JUDGE_TIMEOUT = int(os.getenv("JUDGE_TIMEOUT", "10"))
JUDGE_MEMORY_LIMIT = int(os.getenv("JUDGE_MEMORY_LIMIT", "512"))
JUDGE_CPU_LIMIT = float(os.getenv("JUDGE_CPU_LIMIT", "1.0"))

# 初始化Redis连接
redis_client = redis.from_url(REDIS_URL)

# 初始化Docker客户端
docker_client = docker.from_env()


class JudgeService:
    """评测服务类"""
    
    def __init__(self):
        self.redis_client = redis_client
        self.docker_client = docker_client
    
    def get_submission(self) -> Dict[str, Any]:
        """从Redis队列获取待评测的提交"""
        try:
            # 从队列中获取提交信息
            submission_data = self.redis_client.blpop("judge_queue", timeout=1)
            if submission_data:
                return json.loads(submission_data[1])
            return None
        except Exception as e:
            print(f"Error getting submission: {e}")
            return None
    
    def update_submission_status(self, submission_id: int, status: str, result: Dict[str, Any] = None):
        """更新提交状态"""
        try:
            update_data = {
                "submission_id": submission_id,
                "status": status,
                "result": result,
                "judged_at": datetime.utcnow().isoformat()
            }
            self.redis_client.publish("submission_updates", json.dumps(update_data))
        except Exception as e:
            print(f"Error updating submission status: {e}")
    
    def create_judge_container(self, code: str, language: str, test_cases: list) -> Dict[str, Any]:
        """创建评测容器"""
        try:
            # 创建临时目录
            workspace_dir = f"/app/judge_workspace/{int(time.time())}"
            os.makedirs(workspace_dir, exist_ok=True)
            
            # 根据语言选择基础镜像
            language_configs = {
                "python": {
                    "image": "python:3.11-slim",
                    "file_extension": ".py",
                    "run_command": "python"
                },
                "cpp": {
                    "image": "gcc:11",
                    "file_extension": ".cpp",
                    "run_command": "./a.out"
                },
                "java": {
                    "image": "openjdk:11-jdk-slim",
                    "file_extension": ".java",
                    "run_command": "java"
                },
                "javascript": {
                    "image": "node:18-slim",
                    "file_extension": ".js",
                    "run_command": "node"
                }
            }
            
            config = language_configs.get(language, language_configs["python"])
            
            # 写入代码文件
            code_file = f"{workspace_dir}/main{config['file_extension']}"
            with open(code_file, "w", encoding="utf-8") as f:
                f.write(code)
            
            # 创建Docker容器
            container = self.docker_client.containers.run(
                config["image"],
                command=f"sleep 3600",  # 保持容器运行
                detach=True,
                volumes={
                    workspace_dir: {"bind": "/workspace", "mode": "rw"}
                },
                mem_limit=f"{JUDGE_MEMORY_LIMIT}m",
                cpu_period=100000,
                cpu_quota=int(JUDGE_CPU_LIMIT * 100000),
                network_disabled=True,
                security_opt=["no-new-privileges"],
                cap_drop=["ALL"]
            )
            
            return {
                "container": container,
                "workspace_dir": workspace_dir,
                "code_file": code_file,
                "config": config
            }
            
        except Exception as e:
            print(f"Error creating judge container: {e}")
            return None
    
    def run_test_case(self, container_info: Dict[str, Any], test_case: Dict[str, Any]) -> Dict[str, Any]:
        """运行单个测试用例"""
        try:
            container = container_info["container"]
            workspace_dir = container_info["workspace_dir"]
            config = container_info["config"]
            
            # 编译代码（如果需要）
            if config["file_extension"] == ".cpp":
                compile_result = container.exec_run(
                    f"cd /workspace && g++ -o main main.cpp -O2 -std=c++11",
                    workdir="/workspace"
                )
                if compile_result.exit_code != 0:
                    return {
                        "status": "compilation_error",
                        "error": compile_result.output.decode()
                    }
            
            # 运行代码
            input_data = test_case["input_data"]
            expected_output = test_case["expected_output"]
            
            # 创建输入文件
            input_file = f"{workspace_dir}/input.txt"
            with open(input_file, "w", encoding="utf-8") as f:
                f.write(input_data)
            
            # 执行代码
            start_time = time.time()
            exec_result = container.exec_run(
                f"cd /workspace && timeout {JUDGE_TIMEOUT}s {config['run_command']} main < input.txt",
                workdir="/workspace"
            )
            execution_time = (time.time() - start_time) * 1000  # 转换为毫秒
            
            # 检查执行结果
            if exec_result.exit_code == 124:  # timeout
                return {
                    "status": "time_limit_exceeded",
                    "execution_time": execution_time
                }
            
            if exec_result.exit_code != 0:
                return {
                    "status": "runtime_error",
                    "error": exec_result.output.decode(),
                    "execution_time": execution_time
                }
            
            # 获取输出
            actual_output = exec_result.output.decode().strip()
            
            # 比较输出
            if actual_output == expected_output:
                return {
                    "status": "accepted",
                    "execution_time": execution_time,
                    "memory_used": 0  # TODO: 获取内存使用情况
                }
            else:
                return {
                    "status": "wrong_answer",
                    "expected": expected_output,
                    "actual": actual_output,
                    "execution_time": execution_time
                }
                
        except Exception as e:
            return {
                "status": "system_error",
                "error": str(e)
            }
    
    def judge_submission(self, submission_data: Dict[str, Any]):
        """评测提交"""
        submission_id = submission_data["id"]
        code = submission_data["code"]
        language = submission_data["language"]
        test_cases = submission_data["test_cases"]
        
        print(f"Judging submission {submission_id}")
        
        try:
            # 更新状态为评测中
            self.update_submission_status(submission_id, "judging")
            
            # 创建评测容器
            container_info = self.create_judge_container(code, language, test_cases)
            if not container_info:
                self.update_submission_status(submission_id, "system_error")
                return
            
            container = container_info["container"]
            
            try:
                # 运行所有测试用例
                results = []
                total_tests = len(test_cases)
                passed_tests = 0
                
                for test_case in test_cases:
                    result = self.run_test_case(container_info, test_case)
                    results.append(result)
                    
                    if result["status"] == "accepted":
                        passed_tests += 1
                    elif result["status"] in ["compilation_error", "runtime_error", "system_error"]:
                        # 遇到错误，停止评测
                        break
                
                # 计算最终结果
                if passed_tests == total_tests:
                    final_status = "accepted"
                elif any(r["status"] == "compilation_error" for r in results):
                    final_status = "compilation_error"
                elif any(r["status"] == "runtime_error" for r in results):
                    final_status = "runtime_error"
                elif any(r["status"] == "time_limit_exceeded" for r in results):
                    final_status = "time_limit_exceeded"
                else:
                    final_status = "wrong_answer"
                
                # 计算平均执行时间
                execution_times = [r.get("execution_time", 0) for r in results if "execution_time" in r]
                avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
                
                # 更新结果
                result_data = {
                    "status": final_status,
                    "passed_tests": passed_tests,
                    "total_tests": total_tests,
                    "execution_time": avg_execution_time,
                    "test_results": results
                }
                
                self.update_submission_status(submission_id, final_status, result_data)
                
            finally:
                # 清理容器
                try:
                    container.stop()
                    container.remove()
                except:
                    pass
                
                # 清理工作目录
                try:
                    import shutil
                    shutil.rmtree(container_info["workspace_dir"])
                except:
                    pass
                    
        except Exception as e:
            print(f"Error judging submission {submission_id}: {e}")
            self.update_submission_status(submission_id, "system_error")
    
    def run(self):
        """运行评测服务"""
        print("Judge service started")
        
        while True:
            try:
                # 获取待评测的提交
                submission_data = self.get_submission()
                
                if submission_data:
                    # 评测提交
                    self.judge_submission(submission_data)
                else:
                    # 没有待评测的提交，等待一段时间
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                print("Judge service stopped")
                break
            except Exception as e:
                print(f"Error in judge service: {e}")
                time.sleep(1)


if __name__ == "__main__":
    judge_service = JudgeService()
    judge_service.run() 