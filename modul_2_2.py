# -*- coding: utf-8 -*-
"""02_clusteringResult_step [DONE].ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/18_HR_X9_jEwlu8ozdEjMqmr9Y4BlowiV

# Load Data Clustering
"""

import pandas as pd
cluster1 = pd.read_csv('cluster_1.csv')
cluster2 = pd.read_csv('cluster_2.csv')
cluster3 = pd.read_csv('cluster_3.csv')
cluster4 = pd.read_csv('cluster_4.csv')
cluster5 = pd.read_csv('cluster_5.csv')
cluster6 = pd.read_csv('cluster_6.csv')
cluster7 = pd.read_csv('cluster_7.csv')

# Mengganti nilai kolom 'cluster' menjadi 1 pada DataFrame kluster 11
cluster1.loc[:, 'cluster'] = 1

cluster1.head()

cluster1.info()

cluster2.loc[:, 'cluster'] = 2

cluster2.head()

cluster2.info()

cluster3.loc[:, 'cluster'] = 3

cluster3.head()

cluster3.info()

cluster4.loc[:, 'cluster'] = 4

cluster4.head()

cluster4.info()

cluster5.loc[:, 'cluster'] = 5

cluster5.head()

cluster5.info()

cluster6.loc[:, 'cluster'] = 6

cluster6.head()

cluster6.info()

cluster7 = cluster7.assign(cluster=7)

cluster7.head()

cluster7.info()

"""# Gabungkan Semua Data"""

merged_clusters = pd.concat([cluster1, cluster2, cluster3, cluster4, cluster5, cluster6, cluster7], ignore_index=True)

# Menyimpan data gabungan ke file CSV
merged_clusters.to_csv('datasetWclusters.csv', index=False)

merged_clusters

"""# WORDCLOUD"""

#Wordcloud untuk tiap cluster
from wordcloud import WordCloud
import matplotlib.pyplot as plt
for i in range(1,8):
    # Ambil kolom teks dari dataset dalam kluster tertentu
    cluster = merged_clusters[merged_clusters['cluster'] == i]
    text_column = 'komentarClean'  # Ganti dengan nama kolom teks dalam dataset Anda
    text = ' '.join(cluster[text_column])

    # Buat objek WordCloud dengan parameter yang diinginkan
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='white',
    )

    # Generate word cloud dari teks dalam kluster tertentu
    wordcloud.generate(text)

    # Tampilkan word cloud untuk kluster tertentu
    plt.figure(figsize=(8, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(f'Word Cloud Cluster {i}')
    plt.show()

"""# Nilai Silhouette Coefficient"""

from sklearn.metrics import silhouette_score

labels = merged_clusters['cluster']
# X adalah data Anda
# labels adalah label kluster yang diberikan hasil dari algoritma clustering
silhouette_avg = silhouette_score(X, labels)

print("Silhouette Coefficient:", silhouette_avg)

from sklearn.metrics import silhouette_samples

# Mendapatkan label kluster dari dataset
labels = merged_clusters['cluster'].values

# Menghitung nilai Silhouette untuk setiap sampel
silhouette_vals = silhouette_samples(X, labels)

# Mengelompokkan nilai Silhouette berdasarkan kluster
silhouette_cluster = [[] for _ in range(max(labels) + 1)]
for i in range(len(silhouette_vals)):
    silhouette_cluster[labels[i]].append(silhouette_vals[i])

# Menghitung nilai rata-rata Silhouette untuk setiap kluster
silhouette_means = [pd.Series(vals).mean() for vals in silhouette_cluster]

# Menampilkan nilai Silhouette untuk setiap kluster
for cluster, val in enumerate(silhouette_means):
    print(f"Cluster {cluster}: {val}")

import pandas as pd

df = pd.read_csv('datasetWclusters.csv')
df

cluster_counts = df['cluster'].value_counts()
print("Jumlah setiap cluster:")
print(cluster_counts)

"""# DUMP"""

# Menghitung jumlah data train yang diinginkan (misalnya 25%)
train_ratio = 0.25
train_size = int(train_ratio * len(merged_clusters))

# Mengambil sampel acak untuk data train
df_train = merged_clusters.sample(n=train_size, random_state=42)

# Menghilangkan data train dari data lengkap
df_remaining = merged_clusters.drop(df_train.index)

# Menghitung jumlah data test yang akan dibagi menjadi tiga file
test_size = len(df_remaining)
split_ratio = 1 / 3
split_size = int(split_ratio * test_size)

# Membagi data test menjadi tiga bagian
df_test1 = df_remaining.sample(n=split_size, random_state=42)
df_remaining = df_remaining.drop(df_test1.index)

df_test2 = df_remaining.sample(n=split_size, random_state=42)
df_remaining = df_remaining.drop(df_test2.index)

df_test3 = df_remaining

# Menyimpan data train dan tiga bagian data test ke empat file Excel yang berbeda
with pd.ExcelWriter('data_train.xlsx') as writer:
    df_train.to_excel(writer, sheet_name='Data Train', index=False)

with pd.ExcelWriter('data_test1.xlsx') as writer:
    df_test1.to_excel(writer, sheet_name='Data Test 1', index=False)

with pd.ExcelWriter('data_test2.xlsx') as writer:
    df_test2.to_excel(writer, sheet_name='Data Test 2', index=False)

with pd.ExcelWriter('data_test3.xlsx') as writer:
    df_test3.to_excel(writer, sheet_name='Data Test 3', index=False)

merged_clusters

from sklearn.feature_extraction.text import TfidfVectorizer

# Mengambil kolom komentar
comments = merged_clusters['komentarClean'].tolist()

# Membangun representasi numerik dari komentar menggunakan TF-IDF
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(comments)

merged_clusters.head()

dataset = merged_clusters.copy()

dataset.head()

import pandas as pd
from nltk.sentiment import SentimentIntensityAnalyzer

# Inisialisasi SentimentIntensityAnalyzer
sia = SentimentIntensityAnalyzer()


# Fungsi untuk menghitung compound score pada setiap kalimat
def calculate_compound_score(text):
    sentiment_score = sia.polarity_scores(text)
    return sentiment_score['compound']

# Menghitung compound score untuk setiap komentar
dataset['compound_score'] = dataset['komentarClean'].apply(calculate_compound_score)

# Tampilkan dataset dengan total sentimen compound
print(dataset)

# Menambahkan kolom sentimen berdasarkan compound score
dataset['sentimen'] = dataset['compound_score'].apply(lambda x: 'Positif' if x > 0 else 'Negatif')

dataset.head()

dataset.to_csv('HasilSentimen.csv', index=False)

# Menghitung jumlah sentimen negatif terbanyak di setiap cluster
jumlah_sentimen_negatif = dataset[dataset['sentimen'] == 'Negatif'].groupby('cluster').size().reset_index(name='Sentimen_Negatif')
jumlah_sentimen_negatif = jumlah_sentimen_negatif.sort_values('Sentimen_Negatif', ascending=False)

# Menambahkan kolom peringkat
jumlah_sentimen_negatif['Peringkat'] = jumlah_sentimen_negatif['Sentimen_Negatif'].rank(ascending=False)

# Tampilkan hasil ranking jumlah sentimen negatif terbanyak di setiap cluster
print(jumlah_sentimen_negatif)

dataset.to_csv('HasilRank.csv', index=False)

