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

group_keys = {
    'attention_info': ['attention', 'attention_note', 'attention_partial'],
    'ban_info': ['ban_note', 'ban_yna', 'ban_yn_partial'],
    'control_info': ['control', 'control_note', 'control_partial'],
    'limita_info': ['limita', 'limita_note', 'limita_partial'],
}

def clean_dict(row):
    cleaned = {k: v for k, v in row.items() if pd.notnull(v) and str(v).strip() != ''}
    return cleaned if cleaned else None

for new_col, cols in group_keys.items():
    df[new_col] = df[cols].apply(clean_dict, axis=1)

df = df.drop(columns=[col for cols in group_keys.values() for col in cols])

# 분석 대상 국가 정보만 필터링
country_iso_map = {
    "미국": "US", "중국": "CN", "일본": "JP", "러시아": "RU", "우즈베키스탄": "UZ",
    "베트남": "VN", "캐나다": "CA", "호주": "AU", "카자흐스탄": "KZ", "독일": "DE",
    "브라질": "BR", "영국": "GB", "필리핀": "PH", "뉴질랜드": "NZ", "프랑스": "FR",
    "아르헨티나": "AR", "키르기즈공화국": "KG", "태국": "TH", "인도네시아": "ID", "우크라이나": "UA"
}
target_country_names = list(country_iso_map.keys())

filtered_df = df[df['country_name'].isin(target_country_names)].copy()
filtered_df = filtered_df.reset_index(drop=True)
filtered_df = filtered_df.rename(columns={
    'continent': '대륙',
    'country_name': '국가명',
    'wrt_dt': '등록일',
    'attention_info': '여행유의',
    'ban_info': '여행금지',
    'control_info': '여행자제',
    'limita_info': '철수권고',
    })

filtered_df.to_csv('travel_warning.csv', index=False, encoding='utf-8-sig')