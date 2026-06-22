# YouTube English Bot

Bu proje A1-C2 seviyelerinde İngilizce öğrenme videoları üretir:

- İçerik planı ve konuşma metni
- AI görseller veya yerel placeholder görseller
- Edge TTS ile İngilizce seslendirme
- İstersen TTSMaker Pro/Studio API ile daha kaliteli seslendirme
- FFmpeg ile MP4 video
- İsteğe bağlı YouTube otomatik yükleme

## Kurulum

```powershell
cd "C:\Users\User\Documents\otomatik bot\youtube_english_bot"
.\setup.ps1
```

Manuel kurulum isterseniz:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Bu bilgisayarda sistem `python` komutu yoksa Codex’in paketli Python’u ile de çalışır:

```powershell
& "C:\Users\User\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" main.py --level A2 --topic grammar --no-images
```

FFmpeg yoksa Windows'ta kurun:

```powershell
winget install Gyan.FFmpeg
```

## Hızlı Test

İnternet görsel servisi olmadan test:

```powershell
python main.py --level A2 --topic grammar --no-images
```

veya Windows yardımcı scriptiyle:

```powershell
.\run_bot.ps1 -Level A2 -Topic grammar -NoImages
```

Ücretsiz Pollinations görselleriyle:

```powershell
python main.py --level B1 --topic "phrasal verbs"
```

Çıktılar `output/` klasörüne yazılır.

## TTSMaker Hesabını Kullanma

TTSMaker Pro/Studio hesabı otomasyon için API key ister. TTSMaker dokümanına göre Pro/Studio abonelikte API key oluşturup botta kullanıyoruz; Lite plan API desteklemiyor.

1. [TTSMaker API key sayfasını](https://pro.ttsmaker.com/api-platform/api-key-list) açın.
2. API key oluşturun.
3. `.env` dosyasına şunları ekleyin:

```env
TTS_PROVIDER=ttsmaker
TTSMAKER_API_KEY=buraya_api_key
TTSMAKER_VOICE_ID=1480
TTSMAKER_EMOTION_STYLE_KEY=friendly
TTSMAKER_HIGH_QUALITY=1
```

Voice ID için TTSMaker Studio ekranındaki İngilizce seslerden birini seçebilirsiniz. `1480` çok duygulu İngilizce kadın sesi örneği olarak bırakıldı.

## Daha Akıllı İçerik İçin Ollama

Tamamen ücretsiz yerel LLM kullanmak için Ollama kurup bir model indirin:

```powershell
ollama pull llama3.1:8b
```

`.env` içinde:

```env
BOT_PROVIDER=ollama
OLLAMA_MODEL=llama3.1:8b
```

## YouTube Yükleme

1. Google Cloud Console'da YouTube Data API v3 etkinleştirin.
2. OAuth Desktop App credential oluşturun.
3. İndirdiğiniz JSON dosyasını proje klasörüne `client_secret.json` adıyla koyun.
4. İlk yüklemede tarayıcıdan Google izni verin.

```powershell
python main.py --level B2 --topic idioms --upload
```

Varsayılan gizlilik `private`. Yayına almadan önce videoyu kontrol etmek için özellikle böyle ayarlandı.

## Günlük Otomasyon

```powershell
python scheduler.py --hour 10 --run-now
```

YouTube'a otomatik yüklemek için:

```powershell
python scheduler.py --hour 10 --upload
```
