"""使用deepseek API处理AI请求"""

import os
import time
import logging
from typing import Optional
import groq as ai
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)


def log_request_response(request: str, response: str):
    """格式化记录请求和响应日志"""
    logger.info("=" * 80)
    logger.info("请求内容：\n%s", request)
    logger.info("-" * 80)
    logger.info("响应内容：\n%s", response)
    logger.info("=" * 80)


class ReqAI:
    """使用deepseek API处理AI请求"""

    def __init__(self):
        """使用环境变量配置初始化AI客户端"""
        try:
            load_dotenv("PIGEON/config/myenv.env")
            api_key = os.getenv("GROQ_KEY")
            if not api_key:
                raise ValueError("环境变量中未找到API_KEY")
            self.client = ai.Groq(api_key=api_key)
            logger.info("AI客户端初始化成功")
        except Exception as e:
            logger.error(f"初始化AI客户端失败: {str(e)}")
            raise

    def ask_ai(self, your_question: str) -> str:
        """向AI发送问题并返回响应

        参数:
            your_question: 要询问AI的问题

        返回:
            str: AI的响应或错误信息

        异常:
            Exception: 如果API请求失败
        """
        try:
            logger.info(f"正在向AI发送问题: {your_question[:100]}...")
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": your_question,
                    }
                ],
                model="deepseek-r1-distill-llama-70b",
            )
            return self.extract_content(response)
        except Exception as e:
            logger.error(f"AI请求失败: {str(e)}")
            return f"[AI请求错误] {str(e)}"

    @staticmethod
    def extract_content(response) -> str:
        """从AI响应中提取内容并进行错误处理

        参数:
            response: 来自AI API的原始响应

        返回:
            str: 提取的内容或错误信息
        """
        try:
            if not hasattr(response, "choices"):
                raise ValueError("无效的响应结构")

            choices = response.choices
            if not isinstance(choices, list) or len(choices) == 0:
                raise ValueError("无效的选项格式")

            message = choices[0].message
            if not hasattr(message, "content"):
                raise ValueError("消息缺少内容")

            return str(message.content).strip().split("</think>")[-1]

        except Exception as e:
            logger.error(f"提取内容失败: {str(e)}")
            return f"[AI响应错误] {str(e)}"


if __name__ == "__main__":
    question = f"你是什么模型"
    ai = ReqAI()
    print(ai.ask_ai(question))
