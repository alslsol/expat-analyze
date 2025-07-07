import pandas as pd

# 엑셀 로드
def load_raw_data(filepath):
    df_raw = pd.read_excel(filepath, header=None)
    print(f"[load_raw_data] 데이터 로드 완료: {df_raw.shape}")
    return df_raw

# 시작 행 찾기
def find_data_start(df_raw):
    start_idx = df_raw[df_raw.iloc[:,0] == "구분"].index[0]
    print(f"[find_data_start] 데이터 시작 행: {start_idx}")
    return start_idx

# 결측 채우기
def set_header_and_fill(df_raw, start_idx):
    new_header = df_raw.iloc[start_idx]
    df = df_raw.iloc[start_idx+1:].copy()
    df.columns = new_header
    df.iloc[:, 0:4] = df.iloc[:, 0:4].ffill()
    df.columns = ['대륙', '국가', '성별_임시', '항목'] + df.columns.tolist()[4:]
    print(f"[set_header_and_fill] 헤더 지정 및 결측 채움 완료: {df.shape}")
    return df

# 성별 컬럼 생성
def process_gender(df):
    gender = None
    gender_ls = []
    for i in df['성별_임시']:
        if i in ['남자', '여자']:
            gender = i
        gender_ls.append(gender)
    df['성별'] = gender_ls

    df['성별'] = df['성별_임시']
    df['성별'] = df['성별'].where(df['성별'].isin(['남자', '여자', '합계']), pd.NA)
    df['성별'] = df['성별'].ffill()
    df.drop(columns=['성별_임시'], inplace=True)
    print(f"[process_gender] 성별 처리 완료")
    return df

def fill_country(df):
    df['국가'] = df['국가'].fillna('합계')
    print(f"[fill_country] 국가 결측값 채움 완료")
    return df

def melt_data(df):
    id_vars = ['대륙', '국가', '성별', '항목']
    value_vars = [col for col in df.columns if col not in id_vars]
    df_tidy = df.melt(id_vars=id_vars, value_vars=value_vars,
                      var_name='연령대', value_name='값')
    print(f"[melt_data] 데이터 melt 완료: {df_tidy.shape}")
    return df_tidy

def clean_values(df_tidy):
    df_tidy['값'] = (df_tidy['값']
                     .astype(str)
                     .str.replace(',', '')
                     .replace('nan', pd.NA))
    df_tidy['값'] = pd.to_numeric(df_tidy['값'], errors='coerce')
    print(f"[clean_values] 값 전처리 완료, 결측 개수: {df_tidy['값'].isna().sum()}")
    return df_tidy

def filter_summary(df_tidy):
    df_filtered = df_tidy[(df_tidy['성별'] == '합계') & (df_tidy['연령대'] == '합계')].copy()
    print(f"[filter_summary] 성별, 연령대 '합계' 필터링 완료: {df_filtered.shape}")
    return df_filtered

def pivot_wide(df_filtered):
    df_wide = df_filtered.pivot_table(
        index=['대륙', '국가', '성별', '연령대'],
        columns='항목',
        values='값',
        aggfunc='first'
    ).reset_index()
    print(f"[pivot_wide] wide 포맷 변환 완료: {df_wide.shape}")
    print(f"[pivot_wide] 항목 컬럼들: {df_wide.columns.tolist()}")
    return df_wide

def filter_countries(df_wide, country_iso_map):
    target_countries = list(country_iso_map.keys())
    filtered_df_wide = df_wide[df_wide['국가'].isin(target_countries)].copy().reset_index(drop=True)
    print(f"[filter_countries] 대상 국가 필터링 완료: {filtered_df_wide.shape}")
    return filtered_df_wide

# 실행
def load_and_process_election_data(filepath):
    country_iso_map = {
        "미국": "US", "중국": "CN", "일본": "JP", "러시아": "RU", "우즈베키스탄": "UZ",
        "베트남": "VN", "캐나다": "CA", "호주": "AU", "카자흐스탄": "KZ", "독일": "DE",
        "브라질": "BR", "영국": "GB", "필리핀": "PH", "뉴질랜드": "NZ", "프랑스": "FR",
        "아르헨티나": "AR", "키르기즈공화국": "KG", "태국": "TH", "인도네시아": "ID", "우크라이나": "UA"
    }

    df_raw = load_raw_data(filepath)
    start_idx = find_data_start(df_raw)
    df = set_header_and_fill(df_raw, start_idx)
    print(df)
    df = process_gender(df)
    df = fill_country(df)
    df_tidy = melt_data(df)
    df_tidy = clean_values(df_tidy)
    df_filtered = filter_summary(df_tidy)
    df_wide = pivot_wide(df_filtered)
    filtered_df_wide = filter_countries(df_wide, country_iso_map)

    return df_tidy, filtered_df_wide


# 사용 예시
tidy_df, wide_df = load_and_process_election_data('raw_data/21대총선.xlsx')
wide_df.to_csv('21대총선_전처리.csv', index=False, encoding='utf-8-sig')
print(wide_df.head())
