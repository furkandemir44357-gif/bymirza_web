# byMIRZA — Railway Deploy Rehberi

## Adım 1: Groq API Key Al (Ücretsiz)

1. https://console.groq.com adresine git
2. "Sign Up" ile ücretsiz hesap oluştur
3. Sol menüden **API Keys** → **Create API Key** tıkla
4. Anahtarı kopyala ve bir yere kaydet (örn: `gsk_xxxxxxxxxxxx`)

---

## Adım 2: GitHub'a Yükle

1. https://github.com adresine git, hesap oluştur (yoksa)
2. **New Repository** → İsim ver (örn: `bymirza`) → **Create**
3. Dosyaları yükle:
   - `app.py`
   - `requirements.txt`
   - `Procfile`
   - `templates/` klasörü (index.html içinde)

> 💡 Kolay yol: Repo sayfasında "uploading an existing file" linkine tıkla, sürükle bırak.

---

## Adım 3: Railway'e Deploy Et

1. https://railway.app adresine git
2. **"Start a New Project"** tıkla
3. **"Deploy from GitHub repo"** seç
4. GitHub hesabını bağla, `bymirza` reposunu seç
5. Railway otomatik deploy başlatır ✅

---

## Adım 4: Environment Variable Ekle

Railway dashboard'unda:

1. Projeye tıkla → **Variables** sekmesi
2. Şu iki değişkeni ekle:

| Key | Value |
|-----|-------|
| `GROQ_API_KEY` | `gsk_xxxxxxxxxxxx` (Groq'tan aldığın key) |
| `SECRET_KEY` | istediğin rastgele bir şifre (örn: `mirza2024gizli`) |

3. **Deploy** otomatik yeniden başlar.

---

## Adım 5: Linki Al ve Paylaş

1. Railway dashboard → **Settings** → **Domains**
2. **"Generate Domain"** tıkla
3. Sana şöyle bir link verir: `https://bymirza-production.up.railway.app`
4. Bu linki arkadaşına at — bilgisayarın kapalı olsa bile çalışır! 🎉

---

## ⚠️ Önemli Notlar

- **SQLite sorunu:** Railway'de dosya sistemi kalıcı değil (uygulama restart'ta db sıfırlanabilir). Uzun vadede PostgreSQL'e geçmek daha sağlıklı ama şimdilik çalışır.
- **Ücretsiz limit:** Railway'in ücretsiz planında aylık $5 kredi var, küçük kullanımda yeter.
- **Groq limiti:** Ücretsiz planda dakikada 30 istek, günde 14.400 istek — kişisel kullanım için fazlasıyla yeterli.
