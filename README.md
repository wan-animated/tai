# Social Media Uploader (TikTok + Facebook)

Script Python untuk mengupload video ke TikTok dan post status/reels ke Facebook secara otomatis menggunakan Selenium WebDriver dengan dukungan cookies untuk auto-login.

## 🚀 Fitur Utama

### TikTok Uploader:
- ✅ **Auto-upload video** ke TikTok Studio
- 🍪 **Sistem cookies** untuk auto-login
- 🎯 **Selector spesifik** yang telah dioptimasi
- 🔄 **Fallback system** untuk reliability
- 📸 **Screenshot otomatis** saat error
- 🎨 **Colorful logging** untuk monitoring
- 🖥️ **Mode headless** untuk server
- 🔍 **Debug mode** untuk troubleshooting

### Facebook Uploader:
- ✅ **Auto-post status** ke Facebook (text, video, gambar)
- ✅ **Auto-upload reels** ke Facebook
- 🍪 **Sistem cookies terpisah** untuk Facebook
- 🎯 **Selector yang dioptimasi** untuk Facebook
- 🔄 **Multiple fallback selectors**
- 📸 **Screenshot error** untuk debugging
- 🎨 **Logging yang konsisten**
- 🌐 **Dual language support** (EN/ID) untuk reels

### Social Media Uploader (Gabungan):
- 🚀 **Upload ke semua platform** sekaligus
- 📊 **Status report** untuk setiap platform
- 🍪 **Manajemen cookies terpisah**
- ⚙️ **Mode interaktif dan CLI**

## 📦 Instalasi

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Download ChromeDriver (Otomatis)

Script akan otomatis mendownload ChromeDriver yang sesuai menggunakan `webdriver-manager`.

## 🎯 Penggunaan

### 1. TikTok Uploader

#### Mode Command Line:
```bash
# Upload video dengan caption default
python tiktok_uploader.py --video "path/to/video.mp4"

# Upload dengan caption custom
python tiktok_uploader.py --video "video.mp4" --caption "#viral #fyp #trending"

# Mode headless
python tiktok_uploader.py --video "video.mp4" --headless

# Enable debug logging
python tiktok_uploader.py --video "video.mp4" --debug

# Cek status cookies
python tiktok_uploader.py --check-cookies

# Hapus cookies
python tiktok_uploader.py --clear-cookies
```

#### Mode Interaktif:
```bash
python tiktok_uploader.py
```

### 2. Facebook Uploader

#### Mode Command Line:
```bash
# Post status text
python facebook_uploader.py --type status --status "Hello Facebook!"

# Post status dengan media
python facebook_uploader.py --type status --media "video.mp4" --status "Check this out!"

# Upload reels
python facebook_uploader.py --type reels --video "video.mp4" --description "Amazing reels!"

# Mode headless
python facebook_uploader.py --type status --status "Hello!" --headless

# Cek status cookies Facebook
python facebook_uploader.py --check-cookies

# Hapus cookies Facebook
python facebook_uploader.py --clear-cookies
```

#### Mode Interaktif:
```bash
python facebook_uploader.py
```

### 3. Social Media Uploader (Gabungan)

#### Mode Command Line:
```bash
# Upload ke TikTok saja
python social_media_uploader.py --platform tiktok --video "video.mp4" --tiktok-caption "#fyp"

# Post ke Facebook status saja
python social_media_uploader.py --platform facebook-status --facebook-status "Hello World!"

# Upload reels ke Facebook saja
python social_media_uploader.py --platform facebook-reels --video "video.mp4" --facebook-description "Amazing!"

# Upload video ke TikTok + Facebook Reels
python social_media_uploader.py --platform both-video --video "video.mp4" --tiktok-caption "#fyp" --facebook-description "Check this out!"

# Cek semua cookies
python social_media_uploader.py --check-cookies

# Hapus semua cookies
python social_media_uploader.py --clear-cookies
```

#### Mode Interaktif:
```bash
python social_media_uploader.py
```

## 🎯 Selector yang Digunakan

### TikTok Selectors:
- **Upload Button**: Selector khusus untuk tombol upload TikTok
- **Upload Success**: Indikator bahwa video berhasil diproses
- **Caption Input**: Input field untuk caption
- **Post Button**: Tombol untuk publish video

### Facebook Status Selectors:
- **Status Input**: Input field untuk status Facebook
- **Media Upload**: Input/button untuk upload video/gambar
- **Post Button**: Tombol untuk publish status

### Facebook Reels Selectors:
- **Upload Input**: Input file untuk upload video reels
- **Description Input**: Input field untuk deskripsi reels
- **Next/Berikutnya Button**: Tombol navigasi (dual language)
- **Publish/Terbitkan Button**: Tombol publish (dual language)

## 🍪 Sistem Cookies

### Struktur File Cookies:
- **TikTok**: `cookies/tiktok_cookies.json`
- **Facebook**: `cookies/facebook_cookies.json`

### Format JSON:
```json
{
  "timestamp": 1640995200,
  "cookies": [
    {
      "name": "cookie_name",
      "value": "cookie_value",
      "domain": ".tiktok.com",
      "path": "/",
      "expiry": 1672531200
    }
  ]
}
```

### Cara Kerja:
1. **Pertama kali**: Login manual, cookies otomatis disimpan
2. **Selanjutnya**: Auto-login menggunakan cookies tersimpan
3. **Expired**: Otomatis minta login ulang

## 🔧 Konfigurasi Chrome

### Chrome Options yang Digunakan:
- `--headless=new`: Mode headless terbaru
- `--no-sandbox`: Untuk compatibility
- `--disable-dev-shm-usage`: Memory optimization
- `--disable-images`: Disable gambar untuk performa
- `--disable-gpu`: Disable GPU acceleration
- `--disable-extensions`: Disable ekstensi
- `--disable-notifications`: Disable notifikasi
- `--log-level=3`: Suppress logs
- User-Agent realistis untuk menghindari deteksi bot

### Timeout Settings:
- **Login timeout**: 180 detik (3 menit)
- **Processing timeout**: 120 detik (2 menit)
- **Element timeout**: 30 detik
- **Upload timeout**: 10 detik per selector

## 🌐 Facebook Reels Features

### URL yang Digunakan:
```
https://www.facebook.com/reels/create/?surface=PROFILE_PLUS
```

### Dual Language Support:
- **English**: Next, Publish
- **Indonesian**: Berikutnya, Terbitkan

### Upload Process:
1. **File Upload**: Menggunakan input file selector
2. **First Next**: Navigasi ke step berikutnya
3. **Second Next**: Navigasi ke step final
4. **Description**: Mengisi deskripsi reels
5. **Publish**: Mempublikasikan reels

## 🐛 Troubleshooting

### 1. ChromeDriver Issues
```bash
# Update ChromeDriver
pip install --upgrade webdriver-manager
```

### 2. Login Problems
```bash
# Hapus cookies dan login ulang
python tiktok_uploader.py --clear-cookies
python facebook_uploader.py --clear-cookies
```

### 3. Upload Gagal
```bash
# Jalankan dengan debug mode
python tiktok_uploader.py --video "video.mp4" --debug
python facebook_uploader.py --type reels --video "video.mp4" --debug
```

### 4. Selector Tidak Ditemukan
- Cek screenshot di folder `screenshots/`
- Platform mungkin mengubah struktur HTML
- Update selector di kode jika diperlukan

### 5. Facebook Reels Issues
- Pastikan video format didukung (MP4, MOV, AVI)
- Cek ukuran file (max 4GB untuk Facebook)
- Pastikan durasi video sesuai (15 detik - 60 menit)

## 📊 Status Codes

### Success (✅):
- `success: True` - Upload/Post berhasil dikonfirmasi
- `success: False` dengan pesan - Mungkin berhasil tapi tidak terkonfirmasi

### Error (❌):
- File tidak ditemukan (TikTok/Facebook Reels)
- Status text kosong (Facebook Status)
- Login timeout
- Element tidak ditemukan
- Network error
- Video format tidak didukung

## 🔒 Keamanan

- Cookies disimpan secara lokal dalam format JSON
- User-Agent dan headers realistis
- Anti-detection measures
- No hardcoded credentials
- Cookies terpisah untuk setiap platform
- Screenshot error untuk debugging

## 📝 Logging

### Log Levels:
- 🔍 **DEBUG**: Detail teknis (hanya dengan --debug)
- ℹ️ **INFO**: Informasi umum
- ✅ **SUCCESS**: Operasi berhasil
- ⚠️ **WARNING**: Peringatan
- ❌ **ERROR**: Error yang terjadi

### Contoh Output TikTok:
```
ℹ️ Menyiapkan browser...
✅ Browser siap digunakan
✅ Cookies dimuat: 26/29
ℹ️ Navigasi ke TikTok Studio...
ℹ️ Mengupload: video.mp4 (3.07MB)
✅ Elemen ditemukan
✅ Tombol upload diklik
✅ Input file ditemukan
✅ File berhasil diupload
ℹ️ Menunggu video diproses...
✅ Video berhasil diproses
ℹ️ Menambahkan caption...
✅ Caption ditambahkan: #fyp #viral #trending
ℹ️ Mencari tombol post...
✅ Tombol post berhasil diklik!
✅ Video berhasil dipost!
✅ Video berhasil diupload ke TikTok!
ℹ️ Menutup browser...
```

### Contoh Output Facebook Status:
```
ℹ️ Menyiapkan browser untuk Facebook...
✅ Browser siap digunakan
✅ Cookies dimuat: 15/18
ℹ️ Navigasi ke Facebook...
ℹ️ Memposting status: Hello World!
✅ Elemen ditemukan
✅ Status text berhasil dimasukkan
ℹ️ Mencari tombol post...
✅ Tombol post berhasil diklik!
✅ Post berhasil (kembali ke feed)
✅ Status berhasil dipost ke Facebook!
ℹ️ Menutup browser...
```

### Contoh Output Facebook Reels:
```
ℹ️ Menyiapkan browser untuk Facebook...
✅ Browser siap digunakan
✅ Cookies dimuat: 15/18
ℹ️ Navigasi ke Facebook Reels Create...
ℹ️ Memulai upload video reels...
✅ Input upload ditemukan. Mengirim file...
✅ File video berhasil dikirim ke input.
✅ Tombol 'Next' berhasil diklik (index 1)!
✅ Tombol 'Next' berhasil diklik (index 2)!
✅ Deskripsi berhasil diisi
✅ Tombol 'Publish' berhasil diklik (index 2)!
✅ Upload video reels berhasil!
✅ Reels berhasil diupload ke Facebook!
ℹ️ Menutup browser...
```

## 🤝 Kontribusi

Jika menemukan bug atau ingin menambah fitur:
1. Buat issue untuk bug report
2. Fork repository untuk feature request
3. Submit pull request dengan deskripsi jelas

## ⚖️ Disclaimer

Script ini dibuat untuk tujuan edukasi dan otomasi personal. Pastikan mematuhi Terms of Service TikTok dan Facebook serta gunakan dengan bijak.

## 📁 Struktur File

```
├── tiktok_uploader.py          # TikTok uploader
├── facebook_uploader.py        # Facebook uploader (Status & Reels)
├── social_media_uploader.py    # Gabungan semua platform
├── requirements.txt            # Dependencies
├── cookies/                    # Folder cookies
│   ├── tiktok_cookies.json    # Cookies TikTok
│   └── facebook_cookies.json  # Cookies Facebook
├── screenshots/               # Screenshot error
└── README.md                  # Dokumentasi
```

## 🚀 Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Upload ke TikTok**:
   ```bash
   python tiktok_uploader.py --video "your_video.mp4"
   ```

3. **Post status ke Facebook**:
   ```bash
   python facebook_uploader.py --type status --status "Your status here"
   ```

4. **Upload reels ke Facebook**:
   ```bash
   python facebook_uploader.py --type reels --video "your_video.mp4"
   ```

5. **Upload ke semua platform**:
   ```bash
   python social_media_uploader.py
   ```

## 🎯 Platform Support Matrix

| Platform | Status/Text | Video/Reels | Media Support | Cookies | Auto-Login |
|----------|-------------|-------------|---------------|---------|------------|
| TikTok | ❌ | ✅ | Video Only | ✅ | ✅ |
| Facebook | ✅ | ✅ | Video + Image | ✅ | ✅ |

## 🔄 Update History

### v2.1.0 - Facebook Status Media Support
- ✅ Added video/image support for Facebook Status
- ✅ Auto media type detection
- ✅ Enhanced Facebook status with media upload
- ✅ Improved error handling for media files

### v2.0.0 - Facebook Reels Support
- ✅ Added Facebook Reels upload functionality
- ✅ Dual language support (EN/ID) for Facebook
- ✅ Enhanced Facebook uploader with status/reels choice
- ✅ Updated social media uploader for all platforms
- ✅ Improved error handling and logging

### v1.0.0 - Initial Release
- ✅ TikTok video upload
- ✅ Facebook status posting
- ✅ Cookie management system
- ✅ Basic error handling

Selamat menggunakan! 🎉