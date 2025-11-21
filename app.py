import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# SAYFA AYARLARI
st.set_page_config(layout="wide", page_title="Global Growth Engine")
st.title("🌍 Global Investments - Content Command Center")
st.markdown("---")

# 1. GOOGLE SHEETS BAĞLANTISI
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. VERİLERİ ÇEKME (DEBUG MODU)
try:
    # DİKKAT: worksheet ismi Türkçe Excel'de "Sayfa1", İngilizce'de "Sheet1" olur.
    # usecols listesini kaldırdık, belki sütun isimlerin farklıdır diye hepsini çeksin.
    df = conn.read(worksheet="Sheet1", ttl=0) 
    
    st.success("✅ Google Sheets bağlantısı başarılı!") # Bağlanırsa bunu göreceksin
    st.write("Çekilen Sütunlar:", df.columns.tolist()) # Sütun isimlerini kontrol et
    
    df = df.dropna(how="all")
    
except Exception as e:
    st.error(f"⚠️ KRİTİK HATA DETAYI: {str(e)}") # Gerçek hatayı buraya yazacak
    st.code(f"Hata Türü: {type(e).__name__}")
    st.stop()

# 3. SIDEBAR (FİLTRELER)
with st.sidebar:
    st.header("Filtreler")
    
    # Market Filtresi
    if 'Market' in df.columns:
        unique_markets = df['Market'].unique().tolist()
        selected_market = st.selectbox("Pazar Seç", ["Tümü"] + unique_markets)
    else:
        selected_market = "Tümü"

    # Persona Filtresi
    if 'Persona' in df.columns:
        unique_personas = df['Persona'].unique().tolist()
        selected_persona = st.selectbox("Persona Seç", ["Tümü"] + unique_personas)
    else:
        selected_persona = "Tümü"
        
    if st.button("🔄 Yenile"):
        st.cache_data.clear()
        st.rerun()

# 4. VERİ FİLTRELEME
filtered_df = df.copy()
if selected_market != "Tümü":
    filtered_df = filtered_df[filtered_df['Market'] == selected_market]
if selected_persona != "Tümü":
    filtered_df = filtered_df[filtered_df['Persona'] == selected_persona]

# En yeni içerik en üstte görünsün (Ters sıralama)
filtered_df = filtered_df.iloc[::-1]

# 5. DASHBOARD KARTLARI
for index, row in filtered_df.iterrows():
    with st.container():
        c1, c2 = st.columns([2, 1])
        
        # SOL KOLON: METİN İÇERİKLERİ
        with c1:
            title = row.get('Title') if pd.notna(row.get('Title')) else "Başlıksız İçerik"
            st.subheader(f"📄 {title}")
            
            meta_info = f"**Tarih:** {row.get('Date')} | **Pazar:** {row.get('Market')} | **Persona:** {row.get('Persona')}"
            st.caption(meta_info)
            
            with st.expander("📝 Blog Yazısını Oku"):
                st.markdown(row.get('Blog_Content', 'İçerik Yok'))
                
            with st.expander("📢 Sosyal Medya Metinleri"):
                st.text(row.get('Social_Caption', 'Caption Yok'))

        # SAĞ KOLON: GÖRSEL VE ONAY
        with c2:
            img_url = row.get('Image_URL')
            if pd.notna(img_url) and str(img_url).startswith('http'):
                st.image(img_url, caption="AI Generated Image")
            else:
                st.info("Görsel Yok / Link Bozuk")
            
            # Onay Butonları (Görsel Amaçlı)
            b1, b2 = st.columns(2)
            with b1:
                st.button("✅ Yayınla", key=f"pub_{index}")
            with b2:
                st.button("❌ Sil", key=f"del_{index}")
        
        st.divider()

