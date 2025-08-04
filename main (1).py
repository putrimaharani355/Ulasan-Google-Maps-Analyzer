# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from textblob import TextBlob
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns
import nltk
from collections import Counter
import re

# Setup NLTK
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')

from nltk.corpus import stopwords

# Buat daftar stopword (EN + ID)
stopwords_en = set(stopwords.words('english'))
stopwords_id = set([
    "yang", "dan", "di", "ke", "dari", "untuk", "dengan", "pada", "adalah", "itu",
    "ini", "saya", "kami", "mereka", "tidak", "ya", "atau", "juga", "karena", "sebagai", 
    "oleh", "agar", "sudah", "masih", "saja", "lebih", "dalam", "bisa"
])
custom_stopwords = stopwords_en.union(stopwords_id)

st.set_page_config(page_title="Google Maps Review Analyzer", layout="wide")
st.title("🗺️ Google Maps Review Analyzer")
st.markdown("Analisis dan visualisasi ulasan pelanggan dari Google Maps")

uploaded_file = st.file_uploader("📁 Upload Excel File (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"❌ Gagal membaca file Excel: {e}")
        st.stop()

    # Validasi kolom
    if 'review' not in df.columns or 'rating' not in df.columns:
        st.error("⚠️ File harus memiliki kolom `review` dan `rating`.")
        st.stop()

    df = df[['review', 'rating']].copy()
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df = df.dropna(subset=['review', 'rating'])

    rating_filter = st.slider("⭐ Filter rating:", 1, 5, (1, 5))
    df_filtered = df[df['rating'].between(rating_filter[0], rating_filter[1])]

    st.subheader("📊 Jumlah Review per Rating")
    review_count_by_rating = df_filtered.groupby('rating')['review'].count().reset_index(name='Jumlah Review')
    st.dataframe(review_count_by_rating)

    fig3, ax3 = plt.subplots()
    sns.barplot(data=word_count_by_rating, x='rating', y='review_count_by_rating', palette='viridis', ax=ax3)
    ax3.set_title("Jumlah review per Rating")
    st.pyplot(fig3)

    st.subheader("🔠 Word Cloud")

    # Gabungkan dan bersihkan teks, buang stopword
    words = re.findall(r'\b\w+\b', " ".join(df_filtered['review'].astype(str)).lower())
    filtered_words = [word for word in words if word not in custom_stopwords and len(word) > 2]
    cleaned_text = " ".join(filtered_words)

    wordcloud = WordCloud(width=800, height=400, background_color='white', colormap='plasma').generate(cleaned_text)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)
   
    st.subheader("📋 20 Kata Terbanyak (tanpa stopword)")
    common_words = Counter(filtered_words).most_common(20)
    word_df = pd.DataFrame(common_words, columns=['Word', 'Frequency'])
    st.dataframe(word_df)

    st.subheader("📊 Sentiment Analysis")

    def get_sentiment(text):
        analysis = TextBlob(str(text))
        polarity = analysis.sentiment.polarity
        if polarity > 0:
            return 'Positive'
        elif polarity < 0:
            return 'Negative'
        else:
            return 'Neutral'

    df_filtered['Sentiment'] = df_filtered['review'].apply(get_sentiment)
    sentiment_counts = df_filtered['Sentiment'].value_counts().reset_index()
    sentiment_counts.columns = ['Sentiment', 'Count']

    col1, col2 = st.columns([1, 2])
    with col1:
        st.dataframe(sentiment_counts)
    with col2:
        fig2, ax2 = plt.subplots()
        sns.barplot(data=sentiment_counts, x='Sentiment', y='Count', palette='Set2', ax=ax2)
        ax2.set_title("Distribusi Sentimen")
        st.pyplot(fig2)



else:
    st.info("👈 Silakan upload file Excel (.xlsx) yang memiliki kolom `review` dan `rating`.")
