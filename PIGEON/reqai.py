"""使用ZhipuAI API处理AI请求"""

import os
import time
import logging
from typing import Optional
import zhipuai as ai
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
    """使用ZhipuAI API处理AI请求"""

    def __init__(self):
        """使用环境变量配置初始化AI客户端"""
        try:
            load_dotenv("PIGEON/config/myenv.env")
            api_key = os.getenv("API_KEY")
            if not api_key:
                raise ValueError("环境变量中未找到API_KEY")
            self.client = ai.ZhipuAI(api_key=api_key)
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
                model="glm-4-flash",
                messages=[
                    {"role": "user", "content": your_question},
                ],
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

            return str(message.content).strip()

        except Exception as e:
            logger.error(f"提取内容失败: {str(e)}")
            return f"[AI响应错误] {str(e)}"


if __name__ == "__main__":
    question = f"""
我希望你总结一下下面的内容，给出他们的选择，其中他们的表达左等价于红色方，右等价于蓝色方！我希望你回复的格式是：
【对弈竞猜】名字-选择(可选红、蓝、未知)。

作者名字: 查查尔--d9dc2a75497c4a91b2db1e909a36544d
发布时间: 2024-10-02 23:00:30.888000
竞猜内容:
 【对弈竞猜】10月2日，22:00～24:00，押左（红）
⭐️输了评论区抽6.6r🧧

右边千姬攻击太低，锤子容易掉，续航成问题。左边整体机动性比较强，除非般若魍魉出的好，否则左边大优势，这把我站左边👈
（今日战绩截至目前，4胜2负）
#对弈竞猜# #查查尔语录# #踏雪之卷#
--------------------
作者名字: 林木不是森--b6b5bc8277e34f69aeca018db0081397
发布时间: 2024-10-02 21:03:10.708000
竞猜内容:
 『对弈竞猜』10.2 20:00场次 压蓝/右

🌟输了评论区抽6.6🧧，评论➕关注即可
（在外面，输了回去统一开抽）

🍉没啥好说的，就这样吧，没意思~
#对弈竞猜# #踏雪之卷# #阴阳师#
"""
    ai = ReqAI()
    print(ai.ask_ai(question))
