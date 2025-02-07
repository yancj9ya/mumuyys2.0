import requests
import base64
import cv2
from functools import cached_property

from Mytool.windows import Windows
# 替换为你的 API Key 和 Secret Key
API_KEY = 'your_api_key'
SECRET_KEY = 'your_secret_key'
class ocr_by_bdapi:
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key
        self.ACCESS_TOKEN = self.get_access_token
        self.par_handle=Windows.get_handle('MuMu模拟器12')
        self.child_handle=Windows.get_handleEx(self.par_handle,'MuMuPlayer')
    @cached_property    
    def get_access_token(self):
        token_url = f'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={self.api_key}&client_secret={self.secret_key}'
        response = requests.get(token_url)
        if response.status_code == 200:
            access_token = response.json().get('access_token')
            return access_token
        else:
            raise Exception("获取 Access Token 失败")

    #ACCESS_TOKEN = get_access_token(API_KEY, SECRET_KEY)

    def ocr_image(self, image):
        # 百度 OCR API 端点
        ocr_url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic?access_token={self.ACCESS_TOKEN}"
        
        # 读取图片并编码为 base64
        #with open(image_path, "rb") as f:
        img_data = base64.b64encode(image)
        
        # 请求参数
        params = {"image": img_data}
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        # 发送 POST 请求
        response = requests.post(ocr_url, data=params, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("OCR 请求失败")
    def ocr_text(self, area:list):
        img_bgr=Windows.screenshot(self.child_handle, area)
        result, encoded_image = cv2.imencode('.jpg', img_bgr)
        if not result:raise Exception("图片编码失败")
        return self.ocr_image(encoded_image)   
        
    # 调用 OCR API
    
