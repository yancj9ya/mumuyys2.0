import requests

cookies = {
    "UOR": "www.baidu.com,weibo.com,www.baidu.com",
    "SINAGLOBAL": "4275879129963.7046.1733717584468",
    "SCF": "AkCPjq9--Hy2Z_28p8JpfY3_L4FFBdChnpmkQV_hZQ_OIWNGFDSkuWKjC29EIXqgdgSYCa1Dy1SA-lcrfX0vU6E.",
    "SUB": "_2A25KpC-KDeRhGeFH7FsY-C_JzD2IHXVp2C1CrDV8PUNbmtAbLVDXkW9Neks7lgdZDb2DHtLVA0P0Tzu7gOxgH_gz",
    "SUBP": "0033WrSXqPxfM725Ws9jqgMF55529P9D9WFN2HTXLfsOFYBlVSTfphIo5NHD95QN1KM41KnpSKMpWs4DqcjMi--NiK.Xi-2Ri--ciKnRi-zNS0.N1K.ReK-NeBtt",
    "ALF": "02_1741155546",
    "_s_tentry": "passport.weibo.com",
    "Apache": "8847856965620.26.1738563548295",
    "ULV": "1738563548334:4:1:1:8847856965620.26.1738563548295:1738064562855",
    "XSRF-TOKEN": "RW4NlubENhvIiBJkYNzfr22N",
    "WBPSESS": "RoNLrvolcA-k_IdQHLDZj1FFOGWe9RyAG7jH-0M0NvPKcf2Ng8uZZ4X2I2NhI1nUE1ZDp6XzcbmG_8c-op5CCzmH8UhHlxQcDv9afU9jOO87bzM30p1kLZrPTAME40HVsuuDbMBEaTGkIQv00Mj8tw==",
}

headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "client-version": "v2.47.25",
    # 'cookie': 'UOR=www.baidu.com,weibo.com,www.baidu.com; SINAGLOBAL=4275879129963.7046.1733717584468; SCF=AkCPjq9--Hy2Z_28p8JpfY3_L4FFBdChnpmkQV_hZQ_OIWNGFDSkuWKjC29EIXqgdgSYCa1Dy1SA-lcrfX0vU6E.; SUB=_2A25KpC-KDeRhGeFH7FsY-C_JzD2IHXVp2C1CrDV8PUNbmtAbLVDXkW9Neks7lgdZDb2DHtLVA0P0Tzu7gOxgH_gz; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFN2HTXLfsOFYBlVSTfphIo5NHD95QN1KM41KnpSKMpWs4DqcjMi--NiK.Xi-2Ri--ciKnRi-zNS0.N1K.ReK-NeBtt; ALF=02_1741155546; _s_tentry=passport.weibo.com; Apache=8847856965620.26.1738563548295; ULV=1738563548334:4:1:1:8847856965620.26.1738563548295:1738064562855; XSRF-TOKEN=RW4NlubENhvIiBJkYNzfr22N; WBPSESS=RoNLrvolcA-k_IdQHLDZj1FFOGWe9RyAG7jH-0M0NvPKcf2Ng8uZZ4X2I2NhI1nUE1ZDp6XzcbmG_8c-op5CCzmH8UhHlxQcDv9afU9jOO87bzM30p1kLZrPTAME40HVsuuDbMBEaTGkIQv00Mj8tw==',
    "dnt": "1",
    "priority": "u=1, i",
    "referer": "https://www.weibo.com/1817559703?refer_flag=1001030103_",
    "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Microsoft Edge";v="132"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "server-version": "v2025.01.23.1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
    "x-requested-with": "XMLHttpRequest",
    "x-xsrf-token": "RW4NlubENhvIiBJkYNzfr22N",
}

params = {
    "uid": "1817559703",
    "page": "1",
    "feature": "0",
}

response = requests.get("https://www.weibo.com/ajax/statuses/mymblog", params=params, cookies=cookies, headers=headers)

# print(response.text)


def recursive_search(data, target_key):
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
            result = recursive_search(value, target_key)
            if result is not None:
                return result
    elif isinstance(data, list):
        # 如果 data 是列表，遍历其中的每个项
        for item in data:
            result = recursive_search(item, target_key)
            if result is not None:
                return result
    # 如果没有找到目标键，返回 None
    return None


print(recursive_search(response.json(), "text_raw"))
