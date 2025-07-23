import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import statsmodels.api as sm


import platform
# 운영체제별 폰트 설정
if platform.system() == 'Windows':
    plt.rcParams['font.family'] = 'Malgun Gothic'  # 윈도우는 '맑은 고딕'
elif platform.system() == 'Darwin':  # macOS
    plt.rcParams['font.family'] = 'AppleGothic'
else:
    plt.rcParams['font.family'] = 'NanumGothic'  # Linux 또는 colab 환경

# 마이너스(-) 깨짐 방지
plt.rcParams['axes.unicode_minus'] = False

df = pd.read_csv('raw_data/전처리5.csv')

# df["수출의존도"] = pd.to_numeric(df["수출의존도"].str.replace(",", ""), errors="coerce").astype("float64")
# df["수입의존도"] = pd.to_numeric(df["수입의존도"].str.replace(",", ""), errors="coerce").astype("float64")


cols = [
    'travel_alert',  # 여행경보 단계
    # 'gdp_per_capita',
    'korean_community',  # 재외 한인 수
    'polling_station_count',  # 투표소 수
    # 'a kinship migration',
    # 'Unrelated migration',  # 무연고 이주자 수
    # 'exports_index', 'imports_index',
    'vote_rate1',  # 투표율

    # 연령대별 비율 컬럼 추가
    # 'age_18',
    # 'age_19',
    'age_20-24',
    # 'age_25-29',
    # 'age_30-34',
    # 'age_35-39',
    'age_40-49',
    'age_50-59',
    # 'age_60-69',
    # 'age_70-79',
    # 'age_80'
]


df = df[cols].copy()
df.dropna(inplace=True)

# 상관행렬 계산
# corr = df.corr(numeric_only=True)
# plt.figure(figsize=(10, 8))
# sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
# plt.title("상관관계 행렬")
# plt.show()

# 회귀분석
def run_ols(y_col):
    print(f"\n종속변수: {y_col}")
    X = df.drop(columns=['vote_rate1', #'vote_rate2', 'vote_rate3'
                         ])
    y = df[y_col]
    
    X = sm.add_constant(X)  # 절편 추가
    model = sm.OLS(y, X).fit()
    print(model.summary())

# 반복 분석
for y_col in ['vote_rate1', 
            #   'vote_rate2', 'vote_rate3'
              ]:
    run_ols(y_col)