# 22대 총선 자료 = 07
import pandas as pd

# raw 데이터 가져오기
df_raw = pd.read_excel('raw_data/07_national_vote.xlsx', header=None)

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

# print(df_tidy.head())

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

# 선거인수 0 이상인 국가만 필터링
valid = electors > 0
electors = electors[valid]
voters = voters[valid]

# 전체 투표율 계산
overall_vote_rate = voters.sum() / electors.sum() * 100

# 3. 국가별 총합 계산
total_electors = electors.sum()
total_voters = voters.sum()

# 4. 전체 국가 평균 투표율 계산
# overall_vote_rate = total_voters / total_electors * 100

# 국가별 투표율 계산 (가중 평균)
vote_rate_by_country = (voters / electors) * 100
vote_rate_sorted = vote_rate_by_country.sort_values(ascending=False)

# print(f"전체 국가의 가중 평균 투표율: {overall_vote_rate:.2f}%")
# 27.36% -> 엑셀시트 값과 동일

# print(vote_rate_sorted.head(10))
# print(vote_rate_sorted.tail(50))

# 러시아       100.000000
# 코트디부아르    100.000000
# 카자흐스탄     100.000000
# 적도기니      100.000000
# 에티오피아     100.000000
# 앙골라       100.000000
# 몽골        100.000000
# 오스트리아      66.666667
# 우루과이       62.500000
# 파나마        58.333333
#           ...

#  투표율 하위 50개국
# 체코          33.333333
# 중국          32.978723
# 뉴질랜드        31.288344
# 콜롬비아        30.434783
# 페루          30.303030
# 영국          30.000000
# 캐나다         29.969728
# 아르헨티나       29.160935
# 일본          29.079854
# 이탈리아        28.571429
# 호주          27.906977
# 대만          27.777778
# 합계          27.356543
# 브라질         27.076677
# 노르웨이        25.000000
# 네덜란드        25.000000
# 베네수엘라       25.000000
# 벨기에         25.000000
# 마다가스카르      25.000000
# 파라과이        24.914676
# 코스타리카       23.809524
# 미국          22.328352
# 베트남         21.428571
# 아랍에미리트      20.000000
# 온두라스        20.000000
# 남아프리카공화국    17.647059
# 말레이시아       16.666667
# 멕시코         13.235294
# 스위스          6.250000
# 네팔           0.000000
# 나이지리아        0.000000
# 그리스          0.000000
# 루마니아         0.000000
# 사우디아라비아      0.000000
# 우즈베키스탄       0.000000
# 우간다          0.000000
# 엘살바도르        0.000000
# 슬로바키아        0.000000
# 모로코          0.000000
# 레바논          0.000000
# 브루나이         0.000000
# 이스라엘         0.000000
# 케냐           0.000000
# 캄보디아         0.000000
# 짐바브웨         0.000000
# 자메이카         0.000000
# 이란           0.000000
# 튀르키예         0.000000
# 포르투갈         0.000000
# 핀란드          0.000000


# print(vote_rate_by_country['미국']) # 평균 투표율: 22.32835150016856
# print(vote_rate_by_country['일본']) # 평균 투표율: 29.079854073773813
# print(vote_rate_by_country['독일']) # 평균 투표율: 44.35897435897436

# seaborn 활용해서 시각화-------------
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 한글 폰트 설정
# Windows 기본 폰트 중 하나 설정
plt.rcParams['font.family'] = 'Malgun Gothic'  # 또는 '맑은 고딕'
plt.rcParams['axes.unicode_minus'] = False

# df로 변환
df_plot = vote_rate_by_country.reset_index()
df_plot.columns = ['국가', '투표율']
top20 = df_plot.sort_values('투표율', ascending=False).head(100)

# 그래프 그리기
plt.figure(figsize=(14, 60))
ax = sns.barplot(
    data=top20,
    x='투표율',
    y='국가',
    palette='Blues_d'
)

# 막대 옆에 수치 추가
for i, (value, name) in enumerate(zip(top20['투표율'], top20['국가'])):
    plt.text(
        value + 1,       # 막대 오른쪽에 표시 (살짝 여유를 둠)
        i,               # y축 위치 (barplot은 index 순서대로)
        f'{value:.1f}%', # 소수점 1자리까지
        va='center',
        ha='left',
        fontsize=10)

# 제목/레이 설정
# plt.title('22대 총선 국가별 투표율 상위 100개국', fontsize=16)
# plt.xlabel('투표율 (%)')
# plt.ylabel('국가')
# plt.xlim(0, 100)
# plt.tight_layout()
# plt.savefig('img/vote_rate_top_nation.png', dpi=300, bbox_inches='tight')
# plt.show()

print(df_tidy[df_tidy['국가'] == '미국'].head())