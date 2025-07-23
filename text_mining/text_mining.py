import pandas as pd
from kiwipiepy import Kiwi
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import platform
import seaborn as sns

from wordcloud import WordCloud
import platform
import matplotlib.font_manager as fm


# 운영체제별 한글 폰트 경로 설정
if platform.system() == 'Windows':
    font_path = 'C:/Windows/Fonts/malgun.ttf'
elif platform.system() == 'Darwin':
    font_path = '/System/Library/Fonts/AppleGothic.ttf'
else:  # Linux
    font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'

font_prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()

# 마이너스 깨짐 방지
plt.rcParams['axes.unicode_minus'] = False

# ----

# 1. 데이터 불러오기
kiwi = Kiwi()
df = pd.read_csv('raw_data/커뮤니티.csv')

# 2. 명사 추출 함수 정의
def extract_nouns(text):
    if pd.isnull(text):
        return ""
    tokens = kiwi.analyze(text)[0][0]
    nouns = [word.form for word in tokens if word.tag.startswith("NN")]
    return " ".join(nouns)

# 3. 명사 추출 적용
df["단체소개_nouns"] = df["단체소개"].apply(extract_nouns)

# 4. TF-IDF 벡터화
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(df["단체소개_nouns"])

# 5. 최적 클러스터 수 선택 (Elbow Method 생략)
k = 4
kmeans = KMeans(n_clusters=k, random_state=42)
clusters = kmeans.fit_predict(tfidf_matrix)
df["cluster"] = clusters

# 6. 클러스터별 대표 키워드 출력
def get_top_keywords(tfidf_matrix, cluster_labels, vectorizer, n_terms=10):
    df_result = pd.DataFrame(tfidf_matrix.todense()).groupby(cluster_labels).mean()
    terms = vectorizer.get_feature_names_out()
    for i, row in df_result.iterrows():
        print(f"\nCluster {i}:")
        top_indices = np.argsort(np.array(row))[-n_terms:]
        top_terms = [terms[idx] for idx in reversed(top_indices)]
        print(", ".join(top_terms))

get_top_keywords(tfidf_matrix, clusters, vectorizer)

# 7. 클러스터 수를 국가 단위로 집계
cluster_counts_by_country = df.groupby(['국가', 'cluster']).size().unstack(fill_value=0)
cluster_counts_by_country.columns = [f'cluster_{i}_count' for i in cluster_counts_by_country.columns]
cluster_counts_by_country = cluster_counts_by_country.reset_index()

# 8. 국가별 투표율 데이터 병합
country_df = pd.read_csv("raw_data/전처리5.csv")
cluster_counts_by_country.rename(columns={'국가': 'Country'}, inplace=True)
merged = pd.merge(country_df, cluster_counts_by_country, how='left', on='Country')
merged.fillna(0, inplace=True)

# 9. 회귀 분석용 변수 설정
# y = merged['vote_rate1']

# feature_cols = ['korean_community'] + [col for col in merged.columns if col.startswith('cluster_')]
# X = merged[feature_cols]
# X = sm.add_constant(X)

# model = sm.OLS(y, X).fit()
# print(model.summary())

def plot_cluster_wordclouds(tfidf_matrix, cluster_labels, vectorizer, n_terms=50):
    tfidf_df = pd.DataFrame(tfidf_matrix.toarray())
    labels_df = pd.DataFrame({'cluster': cluster_labels})

    df_mean = tfidf_df.groupby(labels_df['cluster']).mean()
    terms = vectorizer.get_feature_names_out()

    # 운영체제별 폰트 경로 지정
    if platform.system() == 'Windows':
        font_path = 'C:/Windows/Fonts/malgun.ttf'
    elif platform.system() == 'Darwin':
        font_path = '/System/Library/Fonts/AppleGothic.ttf'
    else:
        font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'  # Linux 예시

    for cluster_id, row in df_mean.iterrows():
        top_indices = row.argsort()[-n_terms:]
        words_freq = {terms[i]: row[i] for i in top_indices}

        wordcloud = WordCloud(
            font_path=font_path,
            width=600, height=400,
            background_color='white',
            colormap='tab10'
        ).generate_from_frequencies(words_freq)

        plt.figure(figsize=(8, 6))
        plt.title(f'Cluster {cluster_id} 주요 키워드 워드클라우드')
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.show()
# plot_cluster_wordclouds(tfidf_matrix, clusters, vectorizer)


def plot_pca_scatter(tfidf_matrix, cluster_labels, title="PCA Scatter Plot of Clusters", cmap='tab10'):
    """
    TF-IDF 행렬을 PCA로 2차원 축소 후 클러스터별 산포도 그리기

    Parameters:
    - tfidf_matrix: TF-IDF 희소행렬 (sparse matrix)
    - cluster_labels: 클러스터 번호 리스트 또는 배열
    - title: 그래프 제목 (기본값 있음)
    - cmap: 컬러맵 이름 (기본 'tab10')

    출력: matplotlib 그래프
    """
    # 1. PCA 2차원 축소
    pca = PCA(n_components=2, random_state=42)
    reduced_data = pca.fit_transform(tfidf_matrix.toarray())

    # 2. 산포도 그리기
    plt.figure(figsize=(8, 6))
    scatter = plt.scatter(reduced_data[:, 0], reduced_data[:, 1], c=cluster_labels, cmap=cmap, alpha=0.7)
    plt.xlabel('PCA Component 1')
    plt.ylabel('PCA Component 2')
    plt.title(title)
    plt.legend(*scatter.legend_elements(), title="Clusters")
    plt.grid(True)
    plt.show()
# plot_pca_scatter(tfidf_matrix, clusters)

def plot_cluster_distribution_by_country(cluster_df, top_n=20, exclude_clusters=None):
    """
    국가별 클러스터 분포 스택 바 차트 시각화

    Parameters:
    - cluster_df: cluster_counts_by_country 데이터프레임
    - top_n: 시각화할 상위 국가 수 (단체 수 기준)
    """
    # 제외할 클러스터 없으면 빈 리스트로 초기화
    if exclude_clusters is None:
        exclude_clusters = []

    # 클러스터 컬럼만 선택 (제외할 것 빼고)
    cluster_cols = [col for col in cluster_df.columns if col.startswith('cluster_') and col not in exclude_clusters]

    # 총 단체 수 기준 정렬 (제외된 클러스터도 포함해 계산)
    cluster_df['total'] = cluster_df[[col for col in cluster_df.columns if col.startswith('cluster_')]].sum(axis=1)
    top_countries = cluster_df.sort_values('total', ascending=False).head(top_n)

    # 시각화
    top_countries.set_index('Country', inplace=True)
    top_countries[cluster_cols].plot(
        kind='bar', stacked=True, figsize=(12, 6), colormap='Set2'
    )
    plt.ylabel("한인회 수")
    plt.title(f"국가별 클러스터 분포 (Top {top_n} 국가, 제외: {', '.join(exclude_clusters)})")
    plt.xticks(rotation=45)
    plt.legend(title="Cluster")
    plt.tight_layout()
    plt.show()
# plot_cluster_distribution_by_country(cluster_counts_by_country, top_n=20, exclude_clusters=['cluster_1_count'])

# 히트맵
def plot_cluster_heatmap(cluster_df, top_n=10, exclude_clusters=None, cmap='YlGnBu'):
    cluster_cols = [col for col in cluster_df.columns if col.startswith('cluster_')]

    if exclude_clusters:
        cluster_cols = [col for col in cluster_cols if col not in exclude_clusters]

    # 총 단체 수 기준 상위 국가 추출
    cluster_df['total'] = cluster_df[cluster_cols].sum(axis=1)
    top_countries = cluster_df.sort_values('total', ascending=False).head(top_n)

    heatmap_data = top_countries.set_index('Country')[cluster_cols]

    # 로그 변환 (값이 0이면 log1p(0) = 0 이므로 안전)
    log_heatmap_data = np.log1p(heatmap_data)

    plt.figure(figsize=(10, 6))
    sns.heatmap(
        log_heatmap_data,
        annot=heatmap_data,     # 실제 값 표시
        fmt='g',
        cmap=cmap,
        linewidths=0.5,
        vmin=0,
        vmax=np.log1p(heatmap_data.values.max())
    )
    plt.title(f'상위 {top_n}개국의 클러스터 분포 (로그 스케일 히트맵)')
    plt.ylabel('국가')
    plt.xlabel('클러스터')
    plt.tight_layout()
    plt.show()
# plot_cluster_heatmap(cluster_counts_by_country)