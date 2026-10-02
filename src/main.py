from src.config import settings
from src.exceptions import TaskNotFoundError
from src.logging_config import configure_logging, get_logger
from src.task_service import get_task

configure_logging(settings.log_level)
logger = get_logger(__name__)

def main() -> None:
    logger.info("Starting app: %s", settings.app_name)
    
    try:
        task = get_task(1)  # 尝试获取任务 ID 为 1 的任务
        logger.info(f"Retrieved task: {task.title}, priority: {task.priority}")

        get_task(999)  # 尝试获取任务 ID 为 99 的任务，这将引发 TaskNotFoundError
    except TaskNotFoundError as error:
        logger.error("业务处理失败：%s", error)
        print(f"用户可见提示：任务 {error.task_id} 不存在。")

if __name__ == "__main__":
    main()