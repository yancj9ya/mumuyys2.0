# dynamic_collector.py
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import aiohttp


class DynamicCollector:
    """
    动态信息采集接口

    使用示例：
    async def main():
        async with DynamicCollector() as collector:
            result = await collector.fetch_data()
            print(result)

    asyncio.run(main())
    """

    def __init__(self, uid_mapping: Dict[str, str] = None):
        self.uid_mapping = uid_mapping or {
            "d9dc2a75497c4a91b2db1e909a36544d": "查查尔",
            "b6b5bc8277e34f69aeca018db0081397": "林木不是森",
            # ...其他UID映射
        }
        self.session = None
        self.timeout = 10  # 单次请求超时时间（秒）

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers={"accept": "application/json", "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)..."})
        return self

    async def __aexit__(self, *exc):
        await self.session.close()

    @staticmethod
    def is_time_valid(time: datetime) -> bool:
        """
        判断目标时间是否在当前时间所属的有效偶数小时区间内。

        有效区间定义为：当前小时所属的偶数小时开始的两小时窗口。
        例如：
        - 如果当前时间是14:30，有效区间为14:00-16:00。
        - 如果当前时间是15:45，有效区间为14:00-16:00。
        - 如果当前时间是16:15，有效区间为16:00-18:00。

        :param time: 要判断的目标时间（datetime对象）
        :return: True if 目标时间在有效区间内，否则 False
        """
        # 获取当前时间
        now_time = datetime.now()

        # 首先检查目标时间是否与当前时间在同一天
        if time.date() != now_time.date():
            return False

        # 获取当前小时
        current_hour = now_time.hour

        # 计算当前时间所属的偶数小时区间起始值
        # 例如，current_hour=14 → 14, current_hour=15 →14, current_hour=16 →16
        current_interval_start = current_hour - (current_hour % 2)

        # 确保区间在合理范围内（10:00-24:00）
        if current_interval_start < 10:
            current_interval_start = 10

        # 获取目标时间的小时
        target_hour = time.hour

        # 检查目标时间是否在当前区间内
        return current_interval_start <= target_hour < current_interval_start + 2

    def recursive_search(self, data, target_key):
        """
        递归查找嵌套数据结构中的指定键。

        参数:
        data: 字典或列表，包含待查找的结构。
        target_key: 要查找的目标键。

        返回值:
        如果找到目标键，返回其对应的值；否则返回 None。
        """
        if isinstance(data, dict):
            # 如果 data 是字典，检查是否包含目标键
            if target_key in data:
                return data[target_key]
            # 遍历字典的所有键值对
            for key, value in data.items():
                result = self.recursive_search(value, target_key)
                if result is not None:
                    return result
        elif isinstance(data, list):
            # 如果 data 是列表，遍历其中的每个项
            for item in data:
                result = self.recursive_search(item, target_key)
                if result is not None:
                    return result
        # 如果没有找到目标键，返回 None
        return None

    async def _fetch_single(self, uid: str) -> Optional[dict]:
        """获取单个用户动态"""
        url = "https://inf.ds.163.com/v1/web/feed/basic/getSomeOneFeeds"
        params = {"feedTypes": "1,2,3,4,6,7,10,11", "someOneUid": uid}

        try:
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    return None
                return await response.json()
        except (aiohttp.ClientError, asyncio.TimeoutError):
            return None

    async def _parse_dynamic(self, uid: str) -> Optional[Tuple]:
        """解析动态数据"""
        try:
            data = await asyncio.wait_for(self._fetch_single(uid), self.timeout)
            if not data or data.get("code") != 200:
                return None
            feeds = self.recursive_search(data, "feeds")
            content = None
            create_time = None
            publish_time = None
            for feed in feeds:
                create_time = self.recursive_search(feed, "createTime")
                publish_time = datetime.fromtimestamp(int(create_time) / 1000)
                if self.is_time_valid(publish_time):  # 判断时间是否在有效时间范围内
                    if self.recursive_search(feed, "type") == 2:  # type=2表示分享文字动态
                        content = self.recursive_search(feed, "content")
                        break
                    else:
                        continue

            if content is None or create_time is None:
                return None

            print(f"获取到 {self.uid_mapping.get(uid, '未知用户')} 的动态数据：{content}")

            content_dict = json.loads(content)
            text = self.recursive_search(content_dict, "text")

            return (self.uid_mapping.get(uid, "未知用户"), text.strip(), uid, publish_time.strftime("%Y-%m-%d %H:%M"))
        except (KeyError, json.JSONDecodeError, IndexError, UnboundLocalError):
            return None

    async def fetch_data(self) -> List[Dict]:
        """
        获取有效动态数据

        返回格式：
        [
            {
                "name": "用户名",
                "content": "动态内容",
                "uid": "用户ID",
                "publish_time": "发布时间"
            },
            ...
        ]
        """
        tasks = [self._parse_dynamic(uid) for uid in self.uid_mapping]
        results = await asyncio.gather(*tasks)

        return [{"name": name, "content": content, "uid": uid, "publish_time": pt} for name, content, uid, pt in filter(None, results)]


if __name__ == "__main__":

    async def main():
        # 自定义UID映射（可选）
        custom_uids = {
            "21657a558bdd4ddfb6501298350336e7": "徐清林",
        }

        async with DynamicCollector(uid_mapping=custom_uids) as collector:
            try:
                data = await collector.fetch_data()
                print(f"共获取到{len(data)}条有效动态数据")
                for item in data:
                    print(f"用户：{item['name']}")
                    print(f"内容：{item['content'][:150]}...")
                    print(f"发布时间：{item['publish_time']}\n")
            except Exception as e:
                print(f"数据获取失败: {str(e)}")

    asyncio.run(main())
