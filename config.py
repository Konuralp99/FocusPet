import json
import os

# Versiyon Bilgisi
VERSION = "4.0.2 Alpha (Hotfix)"

# Klasörler
ASSETS_DIR = "assets"
STATS_FILE = "stats.json"

# Pencere İzleme Ayarları
AFK_THRESHOLD_SEC = 45 

# RPG ve Karakter Ayarları
MAX_ENERGY = 100
ENERGY_LOSS_DISTRACTED_PER_MIN = 5
ENERGY_GAIN_FOCUSED_PER_MIN = 3
ENERGY_GAIN_AFK_PER_MIN = 2

# Başlık Anahtar Kelimeleri
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
HEALTH_POSTURE_SEC = 20 * 60
HEALTH_EYE_SEC = 20 * 60
HEALTH_WATER_SEC = 45 * 60

# Eşyalar ve XP Gereksinimleri
XP_PER_LEVEL = 100
XP_FOCUSED_PER_MIN = 10
XP_DISTRACTED_LOSS_PER_MIN = 2

# Varsayılan Veri Yapısı (v4.0 Genişletilmiş)
def get_default_stats():
    return {
        "focused_min": 0,
        "distracted_min": 0,
        "afk_min": 0,
        "xp": 0,
        "level": 1,
        "energy": 100,            # Robotun enerjisi
        "happiness": 100,         # Robotun mutluluk seviyesi
        "history": [],            # [{app: "vscode", duration: 120, time: "20:30", state: "focused"}, ...]
        "daily_quests": [         # Günlük hedefler
            {"id": "study_1h", "title": "1 Saat Odaklan", "goal": 60, "progress": 0, "done": False},
            {"id": "pomo_4", "title": "4 Pomodoro Tamamla", "goal": 4, "progress": 0, "done": False}
        ],
        "items": [],
        "active_evolution": "basic",
        "last_active_date": ""
    }
