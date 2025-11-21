import streamlit as st
import pandas as pd

# SAYFA AYARLARI
st.set_page_config(layout="wide", page_title="Global Growth Engine")
st.title("🌍 Global Investments - Content Command Center")
st.markdown("---")

# =========================================================
# 1. DOĞRUDAN BAĞLANTI (Kütüphanesiz / Secrets Gerektirmez)
# =========================================================

# Senin Sheet ID'n (Linkten aldım)
SHEET_ID = "1tFyLWh3ODIQH2RI64xIuhfws5jn07iHO6LJdaDY3LUo"
# GID genellikle ilk sayfa için 0'dır. Eğer başka sekme ise URL'deki gid=... kısmına bak.
GID = "0" 

# Google'ın özel CSV Export URL formatı
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

@st.cache_data(ttl=5) # 5 saniyede bir yeniler
def load_data():
    try:
        # Pandas doğrudan URL'den okur
        data = pd.read_csv(csv_url)
        # Sütun isimlerindeki boşlukları temizle (Garanti olsun)
        data.columns = data.columns.str.strip()
        return data
    except Exception as e:
        st.error(f"Veri okunamadı. Hata: {e}")
        return pd.DataFrame()

df = load_data()

# =========================================================
# 2. VERİ KONTROLÜ
# =========================================================

if df.empty:
    st.warning("⚠️ Veritabanı boş veya okunamadı.")
    st.info("Lütfen Google Sheet dosyasının 'Herkese Açık' (Viewer) olduğundan emin olun.")
    st.stop()

# =========================================================
# 3. DASHBOARD ARAYÜZÜ
# =========================================================

# SIDEBAR (FİLTRELER)
with st.sidebar:
    st.header("Filtreler")
    
    # Market Filtresi (Eğer Market sütunu varsa)
    if 'Market' in df.columns:
        # NaN (Boş) değerleri temizleyip listele
        unique_markets = df['Market'].dropna().unique().tolist()
        selected_market = st.selectbox("Pazar Seç", ["Tümü"] + unique_markets)
    else:
        selected_market = "Tümü"

    if st.button("🔄 Yenile"):
        st.cache_data.clear()
        st.rerun()

# FİLTRELEME MANTIĞI
filtered_df = df.copy()
if selected_market != "Tümü":
    filtered_df = filtered_df[filtered_df['Market'] == selected_market]

# En yeni en üstte (Ters sıralama)
filtered_df = filtered_df.iloc[::-1]

# KARTLARI GÖSTER
for index, row in filtered_df.iterrows():
    with st.container():
        c1, c2 = st.columns([2, 1])
        
        # SOL KOLON
        with c1:
            # Sütun isimleri Sheet'tekiyle birebir aynı olmalı (Büyük/Küçük harf duyarlı)
            title = row['Title'] if 'Title' in row and pd.notna(row['Title']) else "Başlıksız"
            st.subheader(f"📄 {title}")
            
            # Meta bilgi (Sütun yoksa hata vermesin diye .get kullanıyoruz)
            market_info = row.get('Market', '-')
            persona_info = row.get('Persona', '-')
            date_info = row.get('Date', '-')
            
            st.caption(f"**Tarih:** {date_info} | **Pazar:** {market_info} | **Persona:** {persona_info}")
            
            with st.expander("📝 Blog İçeriği"):
                st.markdown(row.get('Blog_Content', 'İçerik Yok'))
                
            with st.expander("📢 Sosyal Medya"):
                st.text(row.get('Social_Caption', 'Caption Yok'))

        # SAĞ KOLON
        with c2:
            img_url = row.get('Image_URL')
            if pd.notna(img_url) and str(img_url).startswith('http'):
                st.image(str(img_url), caption="AI Görsel")
            else:
                st.info("Görsel Yok")
            
            st.button("✅ Yayınla", key=f"btn_{index}")
        
        st.divider()
