import os, requests
import pandas as pd
from dotenv import load_dotenv
from time import sleep

import urllib3
urllib3.disable_warnings()

from urllib3.util.ssl_ import create_urllib3_context

class TLSAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context()
        # check_hostname 끄기 (SSLContext 속성)
        context.check_hostname = False
        # 필요시 인증서 검증 끄기
        context.verify_mode = 0  # ssl.CERT_NONE 과 동일
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)

# api key
load_dotenv()
TRAVEL_ALARM_API_2 = os.getenv('TRAVEL_ALARM_API_2')

url = 'http://apis.data.go.kr/1262000/TravelWarningServiceV3/getTravelWarningListV3'

params = {
    'serviceKey': 'aBREvpi8LwadkxuME2wYYmaYXplJZk7vJbUy9H9AdQJGuobr8HPi8qhENaFc5Fzsj8kYXn%2BOS07thNkKwx894Q%3D%3D',
    'numOfRows': 100,
    'pageNo': 1,
    'cond[country_nm::EQ]': '미국',
    'returnType': 'JSON',
}

session = requests.Session()
session.mount('http://', TLSAdapter())

response = session.get(url, params=params, verify=False)  # check_hostname 제거
print(response.status_code)
print(response.json())
