import streamlit as st
import pandas as pd
from pyairtable import Api

# SAYFA AYARLARI
st.set_page_config(layout="wide", page_title="Global Growth Engine")

# 1. AIRTABLE BAĞLANTISI (Güvenli Yöntem)
# API Anahtarlarını kodun içine yazmıyoruz, Streamlit Secrets'tan çekeceğiz.
try:
api = Api(st.secrets["AIRTABLE_API_KEY"])
table = api.table(st.secrets["AIRTABLE_BASE_ID"], st.secrets["AIRTABLE_TABLE_NAME"])
except Exception as e:
st.error("Airtable bağlantı hatası! Lütfen Secrets ayarlarını kontrol edin.")
st.stop()

# 2. VERİLERİ ÇEKME FONKSİYONU (Cache kullanarak hızlandırıyoruz)
@st.cache_data(ttl=60) # Her 60 saniyede bir veriyi yeniler
def get_data():
all_records = table.all()
if not all_records:
return pd.DataFrame()
# Airtable verisini Pandas DataFrame'e çevir
data = [r['fields'] for r in all_records]
return pd.DataFrame(data)

# 3. ARAYÜZ BAŞLANGICI
st.title("🌍 Global Investments - Content Command Center")
st.markdown("---")

# Veriyi Yükle
df = get_data()

if df.empty:
st.warning("Henüz veri yok. n8n akışını çalıştırın!")
st.stop()

# 4. SIDEBAR (FİLTRELER)
with st.sidebar:
st.header("Filtreler")

# Market Filtresi
if 'Market' in df.columns:
market_list = ["Tümü"] + list(df['Market'].unique())
selected_market = st.selectbox("Pazar Seç", market_list)
else:
selected_market = "Tümü"

# Persona Filtresi
if 'Persona' in df.columns:
persona_list = ["Tümü"] + list(df['Persona'].unique())
selected_persona = st.selectbox("Persona Seç", persona_list)
else:
selected_persona = "Tümü"

if st.button("🔄 Verileri Yenile"):
st.cache_data.clear()
st.rerun()

# 5. VERİ FİLTRELEME MANTIĞI
filtered_df = df.copy()
if selected_market != "Tümü":
filtered_df = filtered_df[filtered_df['Market'] == selected_market]
if selected_persona != "Tümü":
filtered_df = filtered_df[filtered_df['Persona'] == selected_persona]

# 6. İÇERİK KARTLARI (Dashboard Görünümü)
for index, row in filtered_df.iterrows():
with st.container():
c1, c2 = st.columns([2, 1])

with c1:
status_color = "🟢" if row.get('Status') == 'Published' else "🟡"
st.subheader(f"{status_color} {row.get('Title', 'Başlıksız')}")
st.caption(f"**Market:** {row.get('Market')} | **Persona:** {row.get('Persona')} | **Tarih:** {row.get('Date')}")

with st.expander("📄 Blog İçeriğini Oku"):
st.markdown(row.get('Blog_Content', 'İçerik Yok'))

with st.expander("📱 Sosyal Medya Metinleri"):
st.text(row.get('Social_Caption', 'Caption Yok'))

with c2:
if row.get('Generated_Image_URL'):
st.image(row.get('Generated_Image_URL'), caption="Yapay Zeka Üretimi Görsel")
else:
st.info("Görsel henüz üretilmedi.")

# Butonlar (Şimdilik sadece görsel, backend bağlantısı yok)
b1, b2 = st.columns(2)
with b1:
st.button("✅ Onayla", key=f"approve_{index}")
with b2:
st.button("❌ Reddet", key=f"reject_{index}")

st.divider()