import pandas as pd
import numpy as np
import json


pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)


with open('data/response_1751202671181.json', encoding='utf-8') as f:
    json_data = json.load(f)

items = json_data["response"]["body"]["items"]["item"]

selected_keys = [
    # 여행 유의
    'attention', 'attention_note', 'attention_partial',
    # 여행 금지
    'ban_note', 'ban_yn_partial', 'ban_yna',
    # 여행 자제
    'control', 'control_note', 'control_partial', 
    # 철수 권고
    'limita', 'limita_note', 'limita_partial',
    # 대륙 / 국가명 / iso 코드 / 등록일
    'continent', 'country_name', 'iso_code', 'wrt_dt'
]

filtered_list = [{key: item.get(key, None) for key in selected_keys} for item in items]
df = pd.DataFrame(filtered_list)

# 분석 대상 국가 정보만 필터링
target_countries = [
    "미국", "중국", "일본", "캐나다", "호주", "독일", "브라질", "영국",
    "필리핀", "뉴질랜드", "프랑스", "아르헨티나", "스페인", "페루", "에콰도르",
    "멕시코", "과테말라", "칠레", "싱가포르", "파라과이"
]

df = df[df['country_name'].isin(target_countries)].copy()

# 4. 필요한 컬럼만 추출해서 각각 저장
df_attention = df[["country_name", "wrt_dt", "attention", "attention_note", "attention_partial"]]
df_attention.to_csv("attention_info.csv", index=False, encoding="utf-8-sig")

df_ban = df[["country_name", "wrt_dt", "ban_note", "ban_yn_partial", "ban_yna"]]
df_ban.to_csv("ban_info.csv", index=False, encoding="utf-8-sig")

df_control = df[["country_name", "wrt_dt", "control", "control_note", "control_partial"]]
df_control.to_csv("control_info.csv", index=False, encoding="utf-8-sig")

df_limita = df[["country_name", "wrt_dt", "limita", "limita_note", "limita_partial"]]
df_limita.to_csv("limita_info.csv", index=False, encoding="utf-8-sig")