"""
评测相关的工具函数
"""
import os
import tempfile
import subprocess
import time
from typing import Dict, Any, Optional
from app.models.submission import ProgrammingLanguage


class JudgeUtils:
    """评测工具类"""
    
    @staticmethod
    def get_language_config(language: ProgrammingLanguage) -> Dict[str, Any]:
        """获取编程语言配置"""
        configs = {
            ProgrammingLanguage.PYTHON: {
                "extension": ".py",
                "compile_command": None,
                "run_command": "python",
                "file_name": "main.py"
            },
            ProgrammingLanguage.CPP: {
                "extension": ".cpp",
                "compile_command": "g++ -o main main.cpp -O2 -std=c++11",
                "run_command": "./main",
                "file_name": "main.cpp"
            },
            ProgrammingLanguage.JAVA: {
                "extension": ".java",
                "compile_command": "javac Main.java",
                "run_command": "java Main",
                "file_name": "Main.java"
            },
            ProgrammingLanguage.JAVASCRIPT: {
                "extension": ".js",
                "compile_command": None,
                "run_command": "node",
                "file_name": "main.js"
            },
            ProgrammingLanguage.GO: {
                "extension": ".go",
                "compile_command": "go build -o main main.go",
                "run_command": "./main",
                "file_name": "main.go"
            },
            ProgrammingLanguage.RUST: {
                "extension": ".rs",
                "compile_command": "rustc -o main main.rs",
                "run_command": "./main",
                "file_name": "main.rs"
            }
        }
        
        return configs.get(language, configs[ProgrammingLanguage.PYTHON])
    
    @staticmethod
    def create_temp_directory() -> str:
        """创建临时目录"""
        return tempfile.mkdtemp(prefix="oj_judge_")
    
    @staticmethod
    def write_code_file(directory: str, code: str, language: ProgrammingLanguage) -> str:
        """写入代码文件"""
        config = JudgeUtils.get_language_config(language)
        file_path = os.path.join(directory, config["file_name"])
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)
        
        return file_path
    
    @staticmethod
    def write_input_file(directory: str, input_data: str) -> str:
        """写入输入文件"""
        input_file = os.path.join(directory, "input.txt")
        
        with open(input_file, "w", encoding="utf-8") as f:
            f.write(input_data)
        
        return input_file
    
    @staticmethod
    def compile_code(directory: str, language: ProgrammingLanguage) -> Dict[str, Any]:
        """编译代码"""
        config = JudgeUtils.get_language_config(language)
        
        if not config["compile_command"]:
            return {"success": True, "error": None}
        
        try:
            result = subprocess.run(
                config["compile_command"].split(),
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return {"success": True, "error": None}
            else:
                return {
                    "success": False,
                    "error": result.stderr
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Compilation timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def run_code(
        directory: str,
        language: ProgrammingLanguage,
        input_file: str,
        time_limit: int = 1000,
        memory_limit: int = 512
    ) -> Dict[str, Any]:
        """运行代码"""
        config = JudgeUtils.get_language_config(language)
        
        try:
            # 构建运行命令
            if input_file:
                run_command = f"{config['run_command']} < {input_file}"
            else:
                run_command = config['run_command']
            
            # 使用timeout命令限制执行时间
            full_command = f"timeout {time_limit/1000}s {run_command}"
            
            start_time = time.time()
            result = subprocess.run(
                full_command,
                shell=True,
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=time_limit/1000 + 1
            )
            execution_time = (time.time() - start_time) * 1000  # 转换为毫秒
            
            return {
                "success": True,
                "output": result.stdout,
                "error": result.stderr,
                "execution_time": execution_time,
                "return_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Time limit exceeded",
                "execution_time": time_limit
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "execution_time": 0
            }
    
    @staticmethod
    def compare_output(actual: str, expected: str) -> bool:
        """比较输出结果"""
        # 去除首尾空白字符
        actual = actual.strip()
        expected = expected.strip()
        
        # 简单的字符串比较
        return actual == expected
    
    @staticmethod
    def cleanup_directory(directory: str):
        """清理目录"""
        try:
            import shutil
            shutil.rmtree(directory)
        except Exception:
            pass
    
    @staticmethod
    def get_memory_usage(pid: int) -> Optional[int]:
        """获取进程内存使用量（MB）"""
        try:
            with open(f"/proc/{pid}/status", "r") as f:
                for line in f:
                    if line.startswith("VmRSS:"):
                        # 提取内存使用量（KB）并转换为MB
                        memory_kb = int(line.split()[1])
                        return memory_kb // 1024
        except Exception:
            pass
        
        return None 