import json
import os

# Versiyon Bilgisi
VERSION = "3.0.0 Alpha"

# Klasörler
ASSETS_DIR = "assets"
STATS_FILE = "stats.json"

# Pencere İzleme Ayarları
AFK_THRESHOLD_SEC = 45 

# Başlık Anahtar Kelimeleri (Varsayılanlar)
DEFAULT_WHITELIST = [
    "chatgpt", "openai", "opera", "transkript", "ders", "ödev", "çalışma", "öğren", 
    "new chat", "gpt-4", "gpt-3", "ai", "yapay zeka", "google search", "gemini", "claude",
    "sistem", "dinamik", "kontrol", "soru", "yardım", "sınav", "çözüm", "analiz", "mühendis",
    "github", "stack overflow", "notion", "vscode", "visual studio code", "pycharm"
]

DEFAULT_BLACKLIST = [
    "youtube", "netflix", "twitch", "facebook", "instagram", "twitter", "reddit", 
    "game", "oyun", "disney", "prime video", "valheim", "lol", "valorant"
]

BROWSERS = ["msedge.exe", "chrome.exe", "brave.exe", "opera.exe", "opera_gx.exe", "browser.exe"]

# Pomodoro ve Sağlık Ayarları
POMODORO_WORK_SEC = 25 * 60
POMODORO_BREAK_SEC = 5 * 60
HEALTH_POSTURE_SEC = 20 * 60  # 20 dakikada bir dik oturma uyarısı
HEALTH_EYE_SEC = 20 * 60      # 20-20-20 kuralı (20 saniye uzağa bak)
HEALTH_WATER_SEC = 45 * 60    # 45 dakikada bir su uyarısı

# Eşyalar ve XP Gereksinimleri
XP_PER_LEVEL = 100
XP_FOCUSED_PER_MIN = 10
XP_DISTRACTED_LOSS_PER_MIN = 2

# Varsayılan Veri Yapısı
def get_default_stats():
    return {
        "focused_min": 0,
        "distracted_min": 0,
        "afk_min": 0,
        "xp": 0,
        "level": 1,
        "items": [], # [saksı, lamba vb.]
        "unlocked_evolutions": ["basic"],
        "active_evolution": "basic",
        "streak": 0,
        "last_active_date": ""
    }
