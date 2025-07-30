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

# Tambahan untuk Streamlit Cloud
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

st.set_page_config(page_title="Google Maps Review Analyzer", layout="wide")

st.title("🗺️ Google Maps Review Analyzer")
st.markdown("Analisis dan visualisasi ulasan pelanggan berdasarkan data Google Maps")

uploaded_file = st.file_uploader("📁 Upload Excel File (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"❌ Gagal membaca file Excel: {e}")
        st.stop()

    if 'review' not in df.columns or 'rating' not in df.columns:
        st.error("⚠️ Kolom 'review' dan 'rating' harus ada dalam file Excel.")
        st.stop()

    df = df[['review', 'rating']].dropna()
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df = df.dropna(subset=['rating'])

    rating_filter = st.slider("⭐ Filter rating:", 1, 5, (1, 5))
    df_filtered = df[df['rating'].between(rating_filter[0], rating_filter[1])]

    st.subheader("🔠 Word Cloud")
    text = " ".join(df_filtered['review'].astype(str).tolist())
    wordcloud = WordCloud(width=800, height=400, background_color='white', colormap='plasma').generate(text)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)

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

    st.subheader("📋 Jumlah Kata per Rating")

    # Hitung jumlah kata per review
    df_filtered['Word Count'] = df_filtered['review'].astype(str).apply(lambda x: len(x.split()))

    # Group by rating
    word_count_per_rating = df_filtered.groupby('rating')['Word Count'].sum().reset_index()

    st.dataframe(word_count_per_rating)

    fig3, ax3 = plt.subplots()
    sns.barplot(data=word_count_per_rating, x='rating', y='Word Count', palette='viridis', ax=ax3)
    ax3.set_title("Jumlah Kata per Rating")
    ax3.set_xlabel("Rating")
    ax3.set_ylabel("Total Kata")
    st.pyplot(fig3)

    st.subheader("📋 Tabel Kata Terbanyak")

    words = re.findall(r'\b\w+\b', text.lower())
    common_words = Counter(words).most_common(20)
    word_df = pd.DataFrame(common_words, columns=['Word', 'Frequency'])
    st.dataframe(word_df)

else:
    st.info("👈 Silakan unggah file Excel (.xlsx) berisi kolom `review` dan `rating`.")
