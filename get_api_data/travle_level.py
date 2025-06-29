import os, requests
import pandas as pd
from dotenv import load_dotenv
from time import sleep

# api key
load_dotenv()
TRAVEL_ALARM_API = os.getenv('TRAVEL_ALARM_API')

# 치안
url = 'http://apis.data.go.kr/1262000/SecurityEnvironmentService/getSecurityEnvironmentList'

# 요청 대상 국가 리스트
country_iso_map = {
    "미국": "US",
    # "중국": "CN", "일본": "JP", "러시아": "RU", "우즈베키스탄": "UZ",
    # "베트남": "VN", "캐나다": "CA", "호주": "AU", "카자흐스탄": "KZ", "독일": "DE",
    # "브라질": "BR", "영국": "GB", "필리핀": "PH", "뉴질랜드": "NZ", "프랑스": "FR",
    # "아르헨티나": "AR", "키르기즈공화국": "KG", "태국": "TH", "인도네시아": "ID", "우크라이나": "UA"
}

results = []
missing_alarm_info = []

for kor_name, iso_code in country_iso_map.items():
    params = {
        'serviceKey': TRAVEL_ALARM_API,
        'numOfRows': 100, # 한 페이지 결과 수
        'pageNo': 1, # 페이지 번호
        'cond[country_iso_alp2::EQ]': iso_code,
        # 'cond[country_nm::EQ]': country, # 한글 국가명
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        items = data['response']['body']['items']['item']

        # 하나의 국가에 대해 여러 개가 나올 수 있어서 전부 가져옴
        for item in items:
            alarm_level = item.get('current_travel_alarm')

            if not alarm_level:
                print(f"⚠️ {kor_name}({iso_code}): 경보 정보 없음")
                missing_alarm_info.append(kor_name)
                alarm_level = "정보 없음"

            results.append({
                'country': item.get('country_nm'),
                'alarm_level': item.get('current_travel_alarm'),
                # 'unemployment_rate': item.get('unemployment_rate'),
                # 'suicide_rate': item.get('suicide_death_rate'),
            })
    except Exception as e:
        print(f"{kor_name} 처리 중 오류 발생: {e}")
        continue

    sleep(0.3)


df = pd.DataFrame(results)

df.to_csv('travle_alarm_2.csv', index=False, encoding='utf-8-sig')

# 누락 국가 목록 출력
if missing_alarm_info:
    print("\n여행경보 정보가 누락된 국가 목록:")
    for c in missing_alarm_info:
        print(f"- {c}")
else:
    print("\n모든 국가에서 여행경보 정보가 수집되었습니다!")