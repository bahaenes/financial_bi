import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from dotenv import load_dotenv
import openai
from datetime import datetime

# .env dosyasını yükle
load_dotenv()

# OpenAI API Anahtarını çevresel değişkenlerden al
openai.api_key = os.getenv("OPENAI_API_KEY")

# CSV dosyasını oku
@st.cache_data
def load_data():
    try:
        # CSV dosyasını oku
        df = pd.read_csv('big_tech_stock_prices.csv')
        
        # Tarih sütununu dönüştür
        df['date'] = pd.to_datetime(df['date'])
        
        return df
    except Exception as e:
        st.error(f"Veri yükleme hatası: {str(e)}")
        return None

# Streamlit arayüzü
st.set_page_config(page_title="Teknoloji Hisseleri Analiz Sistemi", layout="wide")

# Ana başlık
st.title("📊 Teknoloji Hisseleri Analiz Sistemi")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("Filtreler")
    
    # Şirket seçimi
    try:
        df = load_data()
        if df is not None:
            companies = sorted(df['stock_symbol'].unique())
            selected_company = st.selectbox(
                "Şirket Seçin",
                companies,
                index=0
            )
            
            # Tarih aralığı seçimi
            date_range = st.date_input(
                "Tarih Aralığı",
                value=(df['date'].min(), df['date'].max()),
                min_value=df['date'].min().date(),
                max_value=df['date'].max().date()
            )
    except:
        st.error("Filtreler yüklenirken hata oluştu.")

# Ana içerik
try:
    df = load_data()
    
    if df is not None and not df.empty:
        # Seçilen şirkete göre filtrele
        filtered_df = df[df['stock_symbol'] == selected_company]
        
        # Tarih aralığına göre filtrele
        filtered_df = filtered_df[
            (filtered_df['date'].dt.date >= date_range[0]) &
            (filtered_df['date'].dt.date <= date_range[1])
        ]
        
        # Veri özeti
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Şirket", selected_company)
        with col2:
            current_price = filtered_df['close'].iloc[-1]
            previous_price = filtered_df['close'].iloc[-2]
            price_change = current_price - previous_price
            st.metric("Son Kapanış", f"${current_price:.2f}", f"{price_change:+.2f}")
        with col3:
            st.metric("En Yüksek", f"${filtered_df['high'].max():.2f}")
        with col4:
            st.metric("En Düşük", f"${filtered_df['low'].min():.2f}")

        # Grafik seçenekleri
        chart_type = st.radio(
            "Grafik Türü",
            ["Mum", "Çizgi"],
            horizontal=True
        )
        
        # Grafikler
        st.subheader("📈 Fiyat Grafiği")
        
        if chart_type == "Mum":
            fig = go.Figure(data=[go.Candlestick(
                x=filtered_df['date'],
                open=filtered_df['open'],
                high=filtered_df['high'],
                low=filtered_df['low'],
                close=filtered_df['close']
            )])
            
            fig.update_layout(
                title=f"{selected_company} Hisse Fiyat Hareketi",
                xaxis_title="Tarih",
                yaxis_title="Fiyat ($)",
                xaxis_rangeslider_visible=False,
                template="plotly_dark"
            )
        else:
            fig = px.line(
                filtered_df,
                x='date',
                y=['close', 'open', 'high', 'low'],
                title=f"{selected_company} Hisse Fiyat Hareketi"
            )
            fig.update_layout(
                xaxis_title="Tarih",
                yaxis_title="Fiyat ($)",
                hovermode='x unified',
                template="plotly_dark"
            )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # İşlem hacmi grafiği
        volume_fig = px.bar(
            filtered_df,
            x='date',
            y='volume',
            title=f"{selected_company} İşlem Hacmi"
        )
        volume_fig.update_layout(
            xaxis_title="Tarih",
            yaxis_title="İşlem Hacmi",
            hovermode='x unified',
            template="plotly_dark"
        )
        st.plotly_chart(volume_fig, use_container_width=True)
        
        # Temel istatistikler
        st.subheader("📊 Temel İstatistikler")
        stats_df = filtered_df[['close', 'volume']].describe()
        st.dataframe(stats_df.style.format("{:.2f}"))
        
        # Ham veri
        if st.checkbox("Ham Veriyi Göster"):
            st.subheader("📋 Ham Veri")
            st.dataframe(filtered_df)
            
    else:
        st.error("Veri yüklenemedi veya boş.")
        st.info("CSV dosyanızın yapısını kontrol edin ve tekrar deneyin.")

except Exception as e:
    st.error(f"Bir hata oluştu: {str(e)}")
    st.info("Lütfen veri dosyasının doğru formatta olduğunu kontrol edin.")

# Footer
st.markdown("---")
st.markdown("*Bu uygulama teknoloji şirketlerinin hisse senedi analizleri için geliştirilmiştir.*") 