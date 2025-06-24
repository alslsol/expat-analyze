# 22대 총선 자료 = 07

import pandas as pd

# raw 데이터 가져오기
df_raw = pd.read_excel('07_national_vote.xlsx', header=None)

# 실제 데이터 시작 행 찾기 (ex: "구분"이라는 글자가 있는 행)
start_idx = df_raw[df_raw.iloc[:,0] == "구분"].index[0]
new_header = df_raw.iloc[start_idx]  # ex) 구분, 합계, 18세...
df = df_raw.iloc[start_idx+1:].copy()
df.columns = new_header

# 지역/성별 결측 채우기
df.iloc[:, 0:4] = df.iloc[:, 0:4].ffill()  # 구분, 성별, 항목
df.columns = ['대륙', '국가', '성별_임시', '항목'] + df.columns.tolist()[4:]

# 혼합된 성별 정보 추출
gender = None
gender_ls = []
for i in df['성별_임시']:
    if i in ['남자', '여자']:
        gender = i
    gender_ls.append(gender)

df['성별'] = gender_ls

# 성별 결측 채우기
df['성별'] = df['성별_임시']
df['성별'] = df['성별'].where(df['성별'].isin(['남자', '여자', '합계']), pd.NA)
df['성별'] = df['성별'].ffill()

# 임시 컬럼 삭제
df.drop(columns=['성별_임시'], inplace=True)

# 국가 결측 채우기
df['국가'] = df['국가'].fillna('합계')

# 숫자 컬럼을 melt 세로형으로 변환
id_vars = ['대륙', '국가', '성별', '항목']
value_vars = [col for col in df.columns if col not in id_vars]  # 연령대 컬럼들
df_tidy = df.melt(id_vars=id_vars, value_vars=value_vars,
                  var_name='연령대', value_name='값')

# 쉼표 제거하고 숫자 변환 (str 타입 변환 후 쉼표 제거)
df_tidy['값'] = df_tidy['값'].astype(str).str.replace(',', '').replace('nan', pd.NA)


df_tidy['값'] = pd.to_numeric(df_tidy['값'], errors='coerce')

print(df_tidy.head())

# 연령대별 투표율 평균
# print(df_tidy[df_tidy['항목'] == '투표율'].groupby(['성별', '연령대'])['값'].mean().unstack())

# # 국가별 총 선거인수
# print(df_tidy[(df_tidy['항목'] == '선거인수') & (df_tidy['연령대'] == '합계')] \
#     .groupby(['대륙', '국가', '성별'])['값'].sum().unstack())

# 투표율 상위 국가
vote_rate = df_tidy[df_tidy['항목'] == '투표율']
country_vote_mean = vote_rate.groupby('국가')['값'].mean()
# max_vote_rate = country_vote_mean.max()
# max_country = country_vote_mean.idxmax()

# print(country_vote_mean.sort_values(ascending=False).head())
# print(country_vote_mean.sort_values(ascending=False).tail())
# ----------------------------
# 22대 총선 투표율 상위 5개국
# 칠레      36.141667
# 독일      35.322222
# 도미니카    31.825000
# 파나마     27.052778
# 우루과이    26.505556

# 22대 총선 투표율 하위 5개국
# 자메이카    0.0
# 이란      0.0
# 튀르키예    0.0
# 포르투갈    0.0
# 핀란드     0.0

# 엑셀: 전체 국가 평균 투표율: 27.4

# print(vote_rate['값'].mean())
# print(vote_rate['값'].isnull().sum())
# print(vote_rate['값'].describe())
# print(vote_rate[vote_rate['값'] == 0])

# vote_rate_total = vote_rate[vote_rate['연령대'] == '합계']
# print(vote_rate_total['값'].mean())

# 투표율 평균
electors = df_tidy[
    (df_tidy['항목'] == '선거인수') & 
    (df_tidy['연령대'] == '합계') & 
    (df_tidy['성별'] == '합계')
].groupby('국가')['값'].sum()

voters = df_tidy[
    (df_tidy['항목'] == '투표자수') & 
    (df_tidy['연령대'] == '합계') & 
    (df_tidy['성별'] == '합계')
].groupby('국가')['값'].sum()

# 3. 국가별 총합 계산
total_electors = electors.sum()
total_voters = voters.sum()

# 4. 전체 국가 평균 투표율 계산
overall_vote_rate = total_voters / total_electors * 100

# 국가별 투표율 계산 (가중 평균)
vote_rate_by_country = (voters / electors) * 100
vote_rate_sorted = vote_rate_by_country.sort_values(ascending=False)

# print(f"전체 국가의 가중 평균 투표율: {overall_vote_rate:.2f}%")
# 27.36% -> 엑셀시트 값과 동일

# print(vote_rate_sorted)
# 러시아       100.0
# 코트디부아르    100.0
# 카자흐스탄     100.0
# 적도기니      100.0
# 에티오피아     100.0
#           ...
# 자메이카        0.0
# 이란          0.0
# 튀르키예        0.0
# 포르투갈        0.0
# 핀란드         0.0

print(vote_rate_by_country['미국']) # 평균 투표율: 22.32835150016856
print(vote_rate_by_country['일본']) # 평균 투표율: 29.079854073773813
print(vote_rate_by_country['독일']) # 평균 투표율: 44.35897435897436

# seaborn 활용해서 시각화해보자