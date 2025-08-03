"""
评测相关的Celery任务
"""
import json
import redis
from celery import current_task
from app.tasks.celery_app import celery_app
from app.core.config import settings

# 初始化Redis连接
redis_client = redis.from_url(settings.redis_url)


@celery_app.task(bind=True)
def judge_submission(self, submission_data: dict):
    """评测提交任务"""
    submission_id = submission_data.get("id")
    
    try:
        # 更新任务状态
        self.update_state(
            state="PROGRESS",
            meta={"submission_id": submission_id, "status": "judging"}
        )
        
        # 将提交发送到评测队列
        judge_data = {
            "submission_id": submission_id,
            "code": submission_data.get("code"),
            "language": submission_data.get("language"),
            "test_cases": submission_data.get("test_cases", []),
            "problem_id": submission_data.get("problem_id")
        }
        
        # 发送到Redis队列
        redis_client.lpush("judge_queue", json.dumps(judge_data))
        
        # 更新任务状态
        self.update_state(
            state="SUCCESS",
            meta={"submission_id": submission_id, "status": "queued"}
        )
        
        return {
            "submission_id": submission_id,
            "status": "queued",
            "message": "Submission queued for judging"
        }
        
    except Exception as e:
        # 更新任务状态为失败
        self.update_state(
            state="FAILURE",
            meta={"submission_id": submission_id, "error": str(e)}
        )
        
        return {
            "submission_id": submission_id,
            "status": "error",
            "error": str(e)
        }


@celery_app.task
def update_submission_result(submission_id: int, result: dict):
    """更新提交结果任务"""
    try:
        # 发布结果更新消息
        update_data = {
            "submission_id": submission_id,
            "result": result,
            "timestamp": "2024-01-01T00:00:00Z"  # TODO: 使用实际时间戳
        }
        
        redis_client.publish("submission_results", json.dumps(update_data))
        
        return {
            "submission_id": submission_id,
            "status": "updated"
        }
        
    except Exception as e:
        return {
            "submission_id": submission_id,
            "status": "error",
            "error": str(e)
        }


@celery_app.task
def cleanup_old_submissions():
    """清理旧提交任务"""
    try:
        # TODO: 实现清理逻辑
        # 删除超过30天的提交记录
        # 清理相关的文件等
        
        return {
            "status": "success",
            "cleaned_count": 0
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@celery_app.task
def update_user_statistics(user_id: int):
    """更新用户统计信息任务"""
    try:
        # TODO: 实现用户统计更新
        # 计算用户的提交数量、通过数量、得分等
        
        return {
            "user_id": user_id,
            "status": "updated"
        }
        
    except Exception as e:
        return {
            "user_id": user_id,
            "status": "error",
            "error": str(e)
        }


@celery_app.task
def update_problem_statistics(problem_id: int):
    """更新题目统计信息任务"""
    try:
        # TODO: 实现题目统计更新
        # 计算题目的提交数量、通过数量、通过率等
        
        return {
            "problem_id": problem_id,
            "status": "updated"
        }
        
    except Exception as e:
        return {
            "problem_id": problem_id,
            "status": "error",
            "error": str(e)
        } 