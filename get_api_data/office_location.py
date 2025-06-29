import os, requests
import pandas as pd
from dotenv import load_dotenv
from time import sleep

# import httpx

load_dotenv()
OFFICE_API = os.getenv('OFFICE_API')

url = 'http://apis.data.go.kr/1262000/EmbassyService2/getEmbassyList2'

# 요청 대상 국가 리스트
country_iso_map = {
    "미국": "US", "중국": "CN", "일본": "JP", "러시아": "RU", "우즈베키스탄": "UZ",
    "베트남": "VN", "캐나다": "CA", "호주": "AU", "카자흐스탄": "KZ", "독일": "DE",
    "브라질": "BR", "영국": "GB", "필리핀": "PH", "뉴질랜드": "NZ", "프랑스": "FR",
    "아르헨티나": "AR", "키르기즈공화국": "KG", "태국": "TH", "인도네시아": "ID", "우크라이나": "UA"
}

results = []

for kor_name, iso_code in country_iso_map.items():
    params = {
        'serviceKey': OFFICE_API,
        'pageNo': '1',
        'numOfRows': '100',
        'cond[country_iso_alp2::EQ]': iso_code
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        items = data['response']['body']['items']['item']

        for item in items:
            results.append({
                '국가명': item.get('country_nm'),
                '국가코드': item.get('country_iso_alp2'),
                '재외공관명': item.get('embassy_kor_nm'),
                # '유형': item.get('embassy_ty_cd_nm'),
                # '재외공관설치일': item.get('embassy_install_dt'),
                '위도': item.get('embassy_lat'),
                '경도': item.get('embassy_lng'),
                '주소': item.get('emblgbd_addr'),
            })
        print(f"✅ {kor_name} 처리 완료")
    except Exception as e:
        print(f"{kor_name}({iso_code}) 처리 중 오류 발생: {e}")
        continue

    sleep(0.3)  # 너무 빠른 요청 방지

# DataFrame으로 만들고 저장
df = pd.DataFrame(results)
df.to_csv('embassy_list.csv', index=False, encoding='utf-8-sig')