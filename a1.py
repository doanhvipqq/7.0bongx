import random, string, time, os, shutil, sys, subprocess
import re
import traceback

# ========== DETECT MÔI TRƯỜNG ==========
IS_TERMUX = os.path.exists("/data/data/com.termux")
IS_LINUX = 'linux' in sys.platform
IS_WINDOWS = os.name == 'nt'

# MÀU
R = '\033[31m'; G = '\033[32m'; Y = '\033[33m'; B = '\033[34m'
C = '\033[36m'; W = '\033[0m'; MG = '\033[1;32m'; MY = '\033[1;33m'

# ========== HÀM SETUP CHO TERMUX ==========
def check_termux_dependencies():
    """Kiểm tra tất cả dependencies trên Termux"""
    issues = []
    
    # Check chromium
    chromium_paths = [
        "/data/data/com.termux/files/usr/bin/chromium-browser",
        "/data/data/com.termux/files/usr/bin/chromium",
    ]
    chromium_ok = any(os.path.exists(p) for p in chromium_paths) or shutil.which("chromium-browser") or shutil.which("chromium")
    if not chromium_ok:
        issues.append("chromium")
    
    # Check chromedriver
    driver_paths = [
        "/data/data/com.termux/files/usr/bin/chromedriver",
    ]
    driver_ok = any(os.path.exists(p) for p in driver_paths) or shutil.which("chromedriver")
    if not driver_ok:
        issues.append("chromedriver")
    
    # Check Python packages
    python_packages = {
        'selenium': 'selenium',
        'requests': 'requests',
        'urllib3': 'urllib3',
    }
    missing_pip = []
    for module_name, pip_name in python_packages.items():
        try:
            __import__(module_name)
        except ImportError:
            missing_pip.append(pip_name)
    
    # Optional packages
    try:
        __import__('fake_useragent')
    except ImportError:
        missing_pip.append('fake-useragent')
    
    if missing_pip:
        issues.append(f"pip:{','.join(missing_pip)}")
    
    return issues

def check_desktop_dependencies():
    """Kiểm tra dependencies trên Windows/Desktop"""
    issues = []
    
    python_packages = {
        'selenium': 'selenium',
        'requests': 'requests',
        'urllib3': 'urllib3',
    }
    missing_pip = []
    for module_name, pip_name in python_packages.items():
        try:
            __import__(module_name)
        except ImportError:
            missing_pip.append(pip_name)
    
    try:
        __import__('fake_useragent')
    except ImportError:
        missing_pip.append('fake-useragent')
    
    if missing_pip:
        issues.append(f"pip:{','.join(missing_pip)}")
    
    # Check chromedriver
    local_driver = "chromedriver.exe" if IS_WINDOWS else "chromedriver"
    driver_ok = os.path.exists(os.path.join(os.getcwd(), local_driver)) or shutil.which("chromedriver")
    if not driver_ok:
        issues.append("chromedriver (cần tải từ https://chromedriver.chromium.org/)")
    
    return issues

def run_termux_setup():
    """Chạy lệnh cài đặt tự động trên Termux"""
    print(f"\n{MG}{'='*55}")
    print(f"        SETUP TỰ ĐỘNG CHO TERMUX")
    print(f"{'='*55}{W}\n")
    
    steps = [
        ("Cap nhat repo Termux", "pkg update -y"),
        ("Cai dat Python", "pkg install -y python"),
        ("Cai dat Chromium + Chromedriver", "pkg install -y chromium"),
        ("Cai dat thu vien Python", "pip install --upgrade selenium requests fake-useragent urllib3"),
    ]
    
    total = len(steps)
    failed = []
    
    for i, (desc, cmd) in enumerate(steps, 1):
        print(f"{Y}[{i}/{total}] {desc}...{W}")
        print(f"{C}  $ {cmd}{W}")
        try:
            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode == 0:
                print(f"{G}  [OK] Thanh cong!{W}\n")
            else:
                print(f"{R}  [!] Co loi (code {result.returncode}){W}")
                if result.stderr:
                    # Chỉ in 3 dòng cuối của error
                    err_lines = result.stderr.strip().split('\n')[-3:]
                    for line in err_lines:
                        print(f"{R}      {line}{W}")
                failed.append(desc)
                print()
        except subprocess.TimeoutExpired:
            print(f"{R}  [!] Timeout (qua 5 phut){W}\n")
            failed.append(desc)
        except Exception as e:
            print(f"{R}  [!] Loi: {e}{W}\n")
            failed.append(desc)
    
    print(f"\n{MG}{'='*55}{W}")
    if not failed:
        print(f"{G}[OK] Setup hoan tat! Tat ca da cai thanh cong.{W}")
    else:
        print(f"{Y}[!] Mot so buoc bi loi:{W}")
        for f in failed:
            print(f"{R}  - {f}{W}")
        print(f"{Y}[TIP] Thu chay lai hoac cai thu cong.{W}")
    print(f"{MG}{'='*55}{W}\n")
    
    input(f"{Y}Nhan Enter de tiep tuc...{W}")

def run_desktop_setup():
    """Chạy lệnh cài đặt trên Desktop (Windows/Linux)"""
    print(f"\n{MG}{'='*55}")
    print(f"        SETUP THU VIEN PYTHON")
    print(f"{'='*55}{W}\n")
    
    cmd = "pip install --upgrade selenium requests fake-useragent urllib3"
    print(f"{Y}[1/1] Cai dat thu vien Python...{W}")
    print(f"{C}  $ {cmd}{W}")
    
    try:
        result = subprocess.run(
            cmd.split(),
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            print(f"{G}  [OK] Thanh cong!{W}")
        else:
            print(f"{R}  [!] Co loi. Thu chay thu cong:{W}")
            print(f"{C}  {cmd}{W}")
    except Exception as e:
        print(f"{R}  [!] Loi: {e}{W}")
    
    print(f"\n{Y}[!] Luu y: Can co Chrome/Chromium va chromedriver phu hop phien ban.{W}")
    print(f"{Y}    Tai chromedriver tai: https://chromedriver.chromium.org/{W}")
    print()
    input(f"{Y}Nhan Enter de tiep tuc...{W}")

def show_setup_prompt():
    """Hiển thị prompt hỏi setup khi khởi động"""
    if IS_TERMUX:
        issues = check_termux_dependencies()
    else:
        issues = check_desktop_dependencies()
    
    if issues:
        print(f"\n{R}{'='*55}")
        print(f"  [!] PHAT HIEN THIEU THU VIEN / CONG CU")
        print(f"{'='*55}{W}")
        for issue in issues:
            if issue.startswith("pip:"):
                pkgs = issue.replace("pip:", "")
                print(f"{Y}  - Python packages: {pkgs}{W}")
            else:
                print(f"{Y}  - {issue}{W}")
        print()
        
        ans = input(f"{G}[?] Ban co muon chay SETUP tu dong khong? (c/k): {W}").strip().lower()
        if ans in ['c', 'y', 'co', 'yes', '']:
            if IS_TERMUX:
                run_termux_setup()
            else:
                run_desktop_setup()
            return True
        else:
            print(f"{Y}[!] Bo qua setup. Co the gap loi khi chay tool.{W}\n")
            time.sleep(1)
            return False
    else:
        print(f"{G}[OK] Tat ca dependencies da san sang!{W}")
        return True

# ========== IMPORT SAU KHI CHECK ==========
# Delay import để setup có thể cài trước
def safe_import():
    """Import các thư viện cần thiết, trả về True nếu OK"""
    global requests, urllib3, logging, webdriver, Service, Options, By, WebDriverWait
    global Select, EC, Keys, UserAgent
    
    try:
        import requests as _requests
        import urllib3 as _urllib3
        import logging as _logging
        
        requests = _requests
        urllib3 = _urllib3
        logging = _logging
        
        logging.getLogger('fake-useragent').setLevel(logging.ERROR)
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    except ImportError as e:
        print(f"{R}[!] Thieu thu vien co ban: {e}{W}")
        print(f"{R}    Chay: pip install requests urllib3{W}")
        return False
    
    try:
        from selenium import webdriver as _wd
        from selenium.webdriver.chrome.service import Service as _Service
        from selenium.webdriver.chrome.options import Options as _Options
        from selenium.webdriver.common.by import By as _By
        from selenium.webdriver.support.ui import WebDriverWait as _Wait, Select as _Select
        from selenium.webdriver.support import expected_conditions as _EC
        from selenium.webdriver.common.keys import Keys as _Keys
        
        globals()['webdriver'] = _wd
        globals()['Service'] = _Service
        globals()['Options'] = _Options
        globals()['By'] = _By
        globals()['WebDriverWait'] = _Wait
        globals()['Select'] = _Select
        globals()['EC'] = _EC
        globals()['Keys'] = _Keys
    except ImportError:
        print(f"{R}[!] Thieu selenium!{W}")
        if IS_TERMUX:
            print(f"{Y}    Chay: pip install selenium{W}")
            print(f"{Y}    Va:   pkg install chromium{W}")
        else:
            print(f"{Y}    Chay: pip install selenium{W}")
        return False
    
    try:
        from fake_useragent import UserAgent as _UA
        globals()['UserAgent'] = _UA
    except ImportError:
        globals()['UserAgent'] = None
    
    # HACK FIX CHO TERMUX: Bypass Selenium Manager
    if IS_TERMUX:
        _patch_selenium_manager()
    
    return True

def _patch_selenium_manager():
    """Patch Selenium Manager cho Termux"""
    try:
        termux_driver = None
        for p in ["/data/data/com.termux/files/usr/bin/chromedriver", shutil.which("chromedriver") or ""]:
            if p and os.path.exists(p):
                termux_driver = p
                break
        
        if termux_driver:
            try:
                from selenium.webdriver.common import selenium_manager
                def patched_driver_location(self, *args, **kwargs):
                    return termux_driver
                selenium_manager.SeleniumManager.driver_location = patched_driver_location
            except (ImportError, AttributeError):
                pass
            
            # Thêm patch cho selenium mới hơn (>= 4.11)
            try:
                from selenium.webdriver.common import driver_finder
                _orig_get_path = driver_finder.DriverFinder.get_path
                def patched_get_path(self, *args, **kwargs):
                    try:
                        return _orig_get_path(self, *args, **kwargs)
                    except Exception:
                        return termux_driver
                driver_finder.DriverFinder.get_path = patched_get_path
            except (ImportError, AttributeError):
                pass
    except Exception:
        pass

# ========== CÁC BIẾN TOÀN CỤC ==========
BASE_PROFILE_DIR = os.path.join(os.getcwd(), "fb_profiles_hidden")
SAVE_DIR = os.path.join(os.getcwd(), "reg_fb_pro")

for d in [BASE_PROFILE_DIR, SAVE_DIR]:
    if not os.path.exists(d): os.makedirs(d)

# TÊN
HOS = ["Nguyễn", "Trần", "Lê", "Phạm", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương"]
TEN_NAM = ["Tuấn", "Dũng", "Hùng", "Nam", "Khánh", "Minh", "Đức", "Trung", "Hiếu", "Hoàng", "Long", "Quân"]
TEN_NU = ["Lan", "Huệ", "Mai", "Trang", "Thảo", "Linh", "Hương", "Hằng", "Thu", "Ngọc", "Vy", "Hân"]

TOKEN_TEMPMAIL = "7446|gUV1YA7SRO7JOv4QbBzYMWRKYRMudibUgfgYCHHz0cdbc4be"
API_KEY_PRIYO = "7jkmE5NM2VS6GqJ9pzlI"
API_KEY_10P = "pdZWgJngWyba9BH2SzOn8wlmNjifV1f"
API_BASE_10P = "https://mail10p.com/api"

# ========== CÁC HÀM CHÍNH ==========
def clean_screen():
    os.system('cls' if IS_WINDOWS else 'clear')
    device = "TERMUX/ANDROID" if IS_TERMUX else ("LINUX" if IS_LINUX else "WINDOWS")
    print(f"{MG}======================================================")
    print(f"         TOOL REG FB  [{device}]")
    print(f"======================================================{W}")

def get_current_ip(proxy_config):
    try:
        proxies = proxy_config['proxy'] if proxy_config and 'proxy' in proxy_config else None
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(
            'http://api.ipify.org?format=json',
            proxies=proxies, timeout=20, headers=headers, verify=False
        )
        return response.json()['ip']
    except:
        try:
            response = requests.get('http://ifconfig.me/ip', proxies=proxies, timeout=15, verify=False)
            return response.text.strip()
        except:
            return "Loi Proxy/Timeout"

def generate_strong_password(length=12):
    characters = string.ascii_letters + string.digits + "!@#$%"
    return "".join(random.choice(characters) for i in range(length))

def parse_proxy(proxy_str):
    """Xử lý Proxy. Nếu để trống sẽ dùng IP máy"""
    if not proxy_str or proxy_str.strip() == "":
        return None
    parts = proxy_str.strip().split(':')
    try:
        if len(parts) == 4:
            p_url = f'http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}'
        else:
            p_url = f'http://{parts[0]}:{parts[1]}'
        return {'proxy': {'http': p_url, 'https': p_url}}
    except:
        return None

# ========== EMAIL FUNCTIONS ==========
def get_mail_fish(session):
    url = 'https://api.tempmail.fish/emails/new-email'
    try:
        res = session.post(url, timeout=15, verify=False)
        if res.status_code == 200:
            data = res.json()
            email = data.get('email')
            auth_key = data.get('authKey')
            if email and auth_key:
                print(f"{G}[FISH-MAIL] Da tao: {C}{email}{W}")
                return email, auth_key
    except Exception as e:
        print(f"{R}[!] Loi tao mail Fish: {e}{W}")
    return None, None

def get_otp_fish(session, email_address, auth_key):
    print(f"{Y}[WAIT] Dang doi OTP tu tempmail.fish...{W}")
    url = 'https://api.tempmail.fish/emails/emails'
    headers = {'Authorization': auth_key}
    params = {'emailAddress': email_address}
    for i in range(15):
        try:
            res = session.get(url, params=params, headers=headers, timeout=10, verify=False)
            if res.status_code == 200:
                emails_list = res.json()
                if isinstance(emails_list, list) and len(emails_list) > 0:
                    content = emails_list[0].get('subject', '') + emails_list[0].get('body', '')
                    otp = "".join(re.findall(r'\d{5,6}', content))
                    if otp:
                        print(f"{G}[OTP] Ma: {C}{otp}{W}")
                        return otp
            time.sleep(7)
            print(f"{Y}[...] Dang quet hom thu lan {i+1}/15...{W}")
        except:
            pass
    return None

def get_mail_priyo(session):
    try:
        url_domain = f"https://free.priyo.email/api/domains/{API_KEY_PRIYO}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = session.get(url_domain, headers=headers, timeout=15, verify=False)
        if response.status_code != 200:
            print(f"{R}[!] Priyo API loi: {response.status_code}{W}")
            return None
        domains = response.json()
        if isinstance(domains, list) and len(domains) > 0:
            url_rand = f"https://free.priyo.email/api/random-email/{API_KEY_PRIYO}"
            res_mail = session.get(url_rand, headers=headers, timeout=15, verify=False).json()
            if isinstance(res_mail, dict):
                email = res_mail.get('email')
            elif isinstance(res_mail, list) and len(res_mail) > 0:
                email = res_mail[0]
            else:
                email = None
            if email:
                print(f"{G}[PRIYO] Mail: {C}{email}{W}")
                return email
    except Exception as e:
        print(f"{R}[!] Loi Priyo: {e}{W}")
    return None

def get_otp_priyo(session, email):
    print(f"{Y}[WAIT] Dang doi ma {email}...{W}")
    for i in range(20):
        try:
            url = f"https://free.priyo.email/api/messages/{email}/{API_KEY_PRIYO}"
            messages = session.get(url, timeout=10, verify=False).json()
            if isinstance(messages, list):
                for msg in messages:
                    subject = msg.get('subject', '')
                    if any(x in subject.lower() for x in ["fb-", "facebook", "ma"]):
                        otp = "".join(re.findall(r'\d+', subject))
                        if len(otp) >= 5:
                            print(f"{G}[OTP] ma: {C}{otp[:6]}{W}")
                            return otp[:6]
            time.sleep(8)
        except:
            pass
    return None

def get_mail_10p(session):
    try:
        url = f"https://mail10p.com/api/emails/{API_KEY_10P}"
        headers = {'Accept': 'application/json', 'User-Agent': 'Mozilla/5.0'}
        response = session.post(url, headers=headers, timeout=20, verify=False)
        if response.status_code == 200:
            res = response.json()
            if res.get('status'):
                email = res['data']['email']
                print(f"{G}[MAIL10P] Da tao Email: {C}{email}{W}")
                return email
    except: pass
    return None

def get_otp_10p(session, email):
    print(f"{Y}[WAIT] Dang doi ma {email}...{W}")
    headers = {'Accept': 'application/json', 'User-Agent': 'Mozilla/5.0'}
    start_time = time.time()
    while time.time() - start_time < 150:
        try:
            url = f"https://mail10p.com/api/messages/{API_KEY_10P}/{email}"
            response = session.get(url, headers=headers, timeout=15, verify=False)
            if response.status_code == 200:
                res = response.json()
                if res.get('status'):
                    messages = res.get('messages', [])
                    for msg in messages:
                        subject = msg.get('subject', '')
                        if any(x in subject for x in ["FB-", "ma xac nhan", "Facebook"]):
                            otp = "".join(filter(str.isdigit, subject))
                            if len(otp) >= 5:
                                print(f"{G}[OTP] Ma: {C}{otp[:5]}{W}")
                                return otp[:5]
            print(f"{Y}[...] Dang load lai hom thu ({int(time.time() - start_time)}s)...{W}")
            time.sleep(10)
        except: pass
    return None

def get_mail_10min(session):
    max_retry = 20
    for i in range(max_retry):
        try:
            url_api = "https://10minutemail.net/address.api.php"
            if i > 0:
                session.get("https://10minutemail.net/address.api.php?new=1", verify=False)
            res = session.get(url_api, timeout=15, verify=False).json()
            email = res.get('mail_get_mail')
            if email and email.endswith("@laoia.com"):
                print(f"{G}[EMAIL] Da lay duoc email: {C}{email}{W}")
                return email
            else:
                print(f"{Y}[...] {email}. Dang doi... ({i+1}){W}")
                time.sleep(2)
        except: continue
    return None

def get_otp_10min(session):
    """Quet OTP tu API 10minutemail.net"""
    print(f"{Y}[WAIT] Dang lay ma...{W}")
    url_api = "https://10minutemail.net/address.api.php"
    for i in range(15):
        try:
            time.sleep(10)
            res = session.get(url_api, timeout=15, verify=False).json()
            mail_list = res.get('mail_list', [])
            for mail in mail_list:
                subject = mail.get('subject', '')
                if "FB-" in subject or "ma xac nhan" in subject:
                    otp = "".join(filter(str.isdigit, subject))
                    if len(otp) >= 5: return otp[:5]
            print(f"{Y}[...] Dang doi thu lan {i+1}/15...{W}")
        except: continue
    return None

# ========== USER AGENT ==========
def get_random_windows_ua():
    """Tao User-Agent Windows dong"""
    win_ver = random.choice(["Windows NT 10.0", "Windows NT 11.0"])
    chrome_major = random.randint(120, 131)
    build_ver = f"{chrome_major}.0.{random.randint(4000, 7000)}.{random.randint(10, 150)}"
    safari_ver = f"{random.randint(530, 537)}.{random.randint(1, 36)}"
    browser_type = random.choice(['chrome', 'edge'])
    base_ua = f"Mozilla/5.0 ({win_ver}; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{build_ver} Safari/{safari_ver}"
    if browser_type == 'edge':
        edge_ver = f"{chrome_major}.0.{random.randint(2000, 3000)}.{random.randint(50, 200)}"
        return f"{base_ua} Edg/{edge_ver}"
    return base_ua

# ========== SETUP DRIVER ==========
def setup_driver(profile_path, proxy_config):
    """Cau hinh trinh duyet - Tuong thich Termux + Desktop"""
    win_ua = get_random_windows_ua()
    print(f"{C}[DEVICE] FAKE UA: {W}{win_ua}")

    chrome_options = Options()

    # === HEADLESS MODE ===
    if IS_TERMUX or IS_LINUX or not os.environ.get('DISPLAY'):
        print(f"{Y}[DEVICE] Che do Headless (An trinh duyet){W}")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")

    # === TERMUX: Setup môi trường trước khi config Chrome ===
    if IS_TERMUX:
        # Tìm Chromium binary
        chromium_paths = [
            "/data/data/com.termux/files/usr/bin/chromium-browser",
            "/data/data/com.termux/files/usr/bin/chromium",
            shutil.which("chromium-browser") or "",
            shutil.which("chromium") or "",
        ]
        chromium_found = None
        for p in chromium_paths:
            if p and os.path.exists(p):
                chromium_found = p
                break
        if chromium_found:
            print(f"{G}[DEVICE] Chromium: {chromium_found}{W}")
            chrome_options.binary_location = chromium_found
        else:
            print(f"{R}[!] Khong tim thay Chromium! Chay: pkg install chromium{W}")
            raise FileNotFoundError("Chromium not found")

        # SET tất cả biến môi trường cần thiết cho Chrome trên Termux
        termux_home = os.environ.get("HOME", "/data/data/com.termux/files/home")
        termux_tmp = os.path.join(termux_home, "tmp")
        termux_cache = os.path.join(termux_home, ".cache", "chromium")
        
        for d in [termux_tmp, termux_cache]:
            os.makedirs(d, exist_ok=True)
        
        os.environ["TMPDIR"] = termux_tmp
        os.environ["HOME"] = termux_home
        os.environ["XDG_CONFIG_HOME"] = os.path.join(termux_home, ".config")
        os.environ["XDG_CACHE_HOME"] = os.path.join(termux_home, ".cache")
        
        # Đặt profile vào thư mục HOME của Termux thay vì cwd
        profile_path = os.path.join(termux_home, "fb_profiles_hidden", os.path.basename(profile_path))
        os.makedirs(profile_path, exist_ok=True)
        
        print(f"{G}[DEVICE] HOME: {termux_home}{W}")
        print(f"{G}[DEVICE] TMPDIR: {termux_tmp}{W}")
        print(f"{G}[DEVICE] Profile: {profile_path}{W}")

    # === CHROME OPTIONS CHUNG ===
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"--user-data-dir={profile_path}")
    chrome_options.add_argument(f'--user-agent={win_ua}')
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--no-first-run")
    chrome_options.add_argument("--ignore-certificate-errors")

    # === OPTIONS RIÊNG CHO TERMUX ===
    if IS_TERMUX:
        # BẮT BUỘC trên Termux - Chrome không thể fork process trên Android
        chrome_options.add_argument("--single-process")
        chrome_options.add_argument("--no-zygote")
        
        # Fix crash
        chrome_options.add_argument("--disable-setuid-sandbox")
        chrome_options.add_argument("--disable-crash-reporter")
        chrome_options.add_argument("--disable-breakpad")
        chrome_options.add_argument("--remote-debugging-port=0")
        
        # Disable features gây lỗi trên Termux
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--disable-background-networking")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--disable-sync")
        chrome_options.add_argument("--disable-translate")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-features=TranslateUI,VizDisplayCompositor,AudioServiceOutOfProcess")
        chrome_options.add_argument("--window-size=480,960")
        
        # Giảm RAM
        chrome_options.add_argument("--js-flags=--max-old-space-size=256")
    else:
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--window-size=1920,1080")

    # === PROXY QUA CHROME OPTIONS ===
    if proxy_config and 'proxy' in proxy_config:
        proxy_url = proxy_config['proxy'].get('http', '')
        if proxy_url:
            proxy_url_clean = proxy_url
            if '@' in proxy_url:
                after_at = proxy_url.split('@')[-1]
                proxy_url_clean = f"http://{after_at}"
                print(f"{Y}[PROXY] Luu y: Proxy co auth co the khong hoat dong tren Termux{W}")
            chrome_options.add_argument(f"--proxy-server={proxy_url_clean}")
            print(f"{G}[PROXY] Da set proxy: {proxy_url_clean}{W}")

    # === EXPERIMENTAL OPTIONS (chi Desktop) ===
    if not IS_TERMUX:
        try:
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
        except Exception:
            pass

    # === TÌM CHROMEDRIVER ===
    service = None
    if IS_TERMUX:
        driver_paths = [
            "/data/data/com.termux/files/usr/bin/chromedriver",
            shutil.which("chromedriver") or "",
        ]
        driver_found = None
        for p in driver_paths:
            if p and os.path.exists(p):
                driver_found = p
                break
        if driver_found:
            print(f"{G}[DEVICE] Chromedriver: {driver_found}{W}")
            # Bật verbose log cho ChromeDriver để debug
            service = Service(
                executable_path=driver_found,
                service_args=["--verbose"],
                log_output=os.path.join(os.environ.get("HOME", "/data/data/com.termux/files/home"), "chromedriver.log")
            )
        else:
            print(f"{R}[!] Khong tim thay chromedriver!{W}")
            raise FileNotFoundError("chromedriver not found")
    else:
        local_driver = "chromedriver.exe" if IS_WINDOWS else "chromedriver"
        current_dir_driver = os.path.join(os.getcwd(), local_driver)
        if os.path.exists(current_dir_driver):
            service = Service(executable_path=current_dir_driver)
        elif shutil.which("chromedriver"):
            service = Service(executable_path=shutil.which("chromedriver"))
        else:
            service = Service()

    # === KHỞI TẠO DRIVER ===
    try:
        print(f"{Y}[DEVICE] Dang khoi tao trinh duyet...{W}")
        
        # In ra tất cả Chrome arguments để debug
        if IS_TERMUX:
            args_list = chrome_options.arguments
            print(f"{C}[DEBUG] Chrome args: {len(args_list)} flags{W}")
            for a in args_list:
                if not a.startswith("--user-agent") and not a.startswith("--user-data"):
                    print(f"{C}  {a}{W}")
        
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print(f"{G}[DEVICE] Trinh duyet da san sang!{W}")
    except Exception as e:
        err_msg = str(e).lower()
        print(f"{R}[ERROR] Loi khoi tao Driver!{W}")
        print(f"{R}[DETAIL] {e}{W}")
        
        if IS_TERMUX:
            print(f"\n{Y}[TIP] Thu cac buoc sau:{W}")
            print(f"{G}  1. pkg update && pkg install chromium{W}")
            print(f"{G}  2. chmod +x /data/data/com.termux/files/usr/bin/chromedriver{W}")
            print(f"{G}  3. chromium-browser --headless --no-sandbox --disable-gpu --dump-dom https://example.com{W}")
            print(f"{Y}     (neu lenh tren KHONG in ra HTML => Chromium bi loi){W}")
            
            # Check verbose log
            log_path = os.path.join(os.environ.get("HOME", "/data/data/com.termux/files/home"), "chromedriver.log")
            if os.path.exists(log_path):
                print(f"\n{Y}[LOG] ChromeDriver log (cuoi file):{W}")
                try:
                    with open(log_path, 'r') as f:
                        lines = f.readlines()
                        for line in lines[-15:]:
                            print(f"{C}  {line.rstrip()}{W}")
                except Exception:
                    pass
            
            # Tự kiểm tra version
            try:
                import subprocess as sp
                cv = sp.run(["chromium-browser", "--version"], capture_output=True, text=True, timeout=5)
                dv = sp.run(["chromedriver", "--version"], capture_output=True, text=True, timeout=5)
                print(f"\n{C}  Chromium : {cv.stdout.strip()}{W}")
                print(f"{C}  Driver   : {dv.stdout.strip()}{W}")
            except Exception:
                pass
            
            # Test thử Chromium trực tiếp
            print(f"\n{Y}[TEST] Dang thu chay Chromium truc tiep...{W}")
            try:
                import subprocess as sp
                test_cmd = [
                    chromium_found or "chromium-browser",
                    "--headless", "--no-sandbox", "--disable-gpu",
                    "--single-process", "--no-zygote",
                    "--dump-dom", "data:text/html,<h1>test</h1>"
                ]
                test_result = sp.run(test_cmd, capture_output=True, text=True, timeout=15)
                if "test" in test_result.stdout:
                    print(f"{G}  [OK] Chromium chay duoc! Loi co the do ChromeDriver.{W}")
                else:
                    print(f"{R}  [FAIL] Chromium KHONG chay duoc.{W}")
                    if test_result.stderr:
                        for line in test_result.stderr.strip().split('\n')[-5:]:
                            print(f"{R}  {line}{W}")
            except Exception as te:
                print(f"{R}  [FAIL] Khong test duoc: {te}{W}")
        else:
            if "permission" in err_msg or "executable" in err_msg:
                print(f"{Y}[TIP] Thu chay: chmod +x $(which chromedriver){W}")

        raise e

    # === ANTI-DETECT BANG JS ===
    try:
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'languages', {get: () => ['vi-VN', 'vi', 'en-US', 'en']});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
                window.chrome = { runtime: {} };
            """
        })
    except Exception:
        try:
            driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
            )
        except Exception:
            print(f"{Y}[WARN] Khong the inject anti-detect JS{W}")

    return driver

def send_keys_slowly(element, text):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.2))

# ========== REG ACCOUNT ==========
def run_one_account(proxy_str, mode="auto", email_manual=None, mail_source="1"):
    proxy_config = parse_proxy(proxy_str)
    mail_session = requests.Session()
    if proxy_config:
        mail_session.proxies = proxy_config['proxy']

    if mode == "auto":
        if mail_source == "2":
            email = get_mail_10p(mail_session)
        elif mail_source == "3":
            email = get_mail_priyo(mail_session)
        elif mail_source == "4":
            email, auth_key_fish = get_mail_fish(mail_session)
        else:
            email = get_mail_10min(mail_session)

        if not email:
            print(f"{R}[!] Khong lay duoc mail. Bo qua.{W}")
            return
    else:
        email = email_manual

    current_ip = get_current_ip(proxy_config)
    print(f"{Y}[IP] IP hien tai: {C}{current_ip}{W}")

    temp_id = random.randint(1000, 9999)
    my_p_path = os.path.join(BASE_PROFILE_DIR, f"pro_{email.split('@')[0]}_{temp_id}")

    driver = None
    try:
        driver = setup_driver(my_p_path, proxy_config)
    except Exception as e:
        print(f"{R}[!] Khong khoi tao duoc trinh duyet: {e}{W}")
        shutil.rmtree(my_p_path, ignore_errors=True)
        return

    wait = WebDriverWait(driver, 30)
    status = "FAILURE"; uid = "N/A"; ck_str = ""; final_url = ""

    try:
        is_nam = random.choice([True, False])
        ho = random.choice(HOS)
        t_dem = random.choice(TEN_NAM if is_nam else TEN_NU)
        t_chinh = random.choice(TEN_NAM if is_nam else TEN_NU)
        full_name = f"{ho} {t_dem} {t_chinh}"
        pw = generate_strong_password()

        print(f"{B}[RUNNING] [{mode.upper()}] {email} | {full_name}{W}")
        driver.get("https://m.facebook.com/reg")
        time.sleep(20)

        send_keys_slowly(wait.until(EC.presence_of_element_located((By.NAME, "firstname"))), f"{t_dem} {t_chinh}")
        send_keys_slowly(driver.find_element(By.NAME, "lastname"), ho)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        print(f"{Y}[WAIT] Da nhap ten...{W}")
        time.sleep(2)

        Select(wait.until(EC.presence_of_element_located((By.ID, "day")))).select_by_value(str(random.randint(1, 28)))
        Select(driver.find_element(By.ID, "month")).select_by_value(str(random.randint(1, 12)))
        Select(driver.find_element(By.ID, "year")).select_by_value(str(random.randint(1995, 2004)))
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        print(f"{Y}[WAIT] Da nhap ngay sinh...{W}")
        time.sleep(2)

        email_el = wait.until(EC.presence_of_element_located((By.NAME, "reg_email__")))
        send_keys_slowly(email_el, email)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        print(f"{Y}[WAIT] Da nhap email...{W}")
        time.sleep(2)

        driver.find_element(By.XPATH, f"//input[@name='sex' and @value='{'2' if is_nam else '1'}']").click()
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        print(f"{Y}[WAIT] Da nhap gioi tinh...{W}")
        time.sleep(2)

        pass_el = wait.until(EC.presence_of_element_located((By.NAME, "reg_passwd__")))
        send_keys_slowly(pass_el, pw)
        pass_el.send_keys(Keys.ENTER)
        print(f"{Y}[WAIT] Da gui dang ky{W}")

        time.sleep(1)
        print(f"{Y}[WAIT] Doi xu ly...{W}")
        time.sleep(13)

        try:
            if "checkpoint" in driver.current_url:
                print(f"{R}[!] Bi Checkpoint! Bo acc!{W}")
                raise Exception("Checkpoint")

            wait_otp = WebDriverWait(driver, 45)
            wait_otp.until(EC.presence_of_element_located((By.NAME, "code")))
            print(f"{G}[OTP] Bat dau lay OTP...{W}")

            if mode == "auto":
                if mail_source == "2":
                    otp = get_otp_10p(mail_session, email)
                elif mail_source == "3":
                    otp = get_otp_priyo(mail_session, email)
                elif mail_source == "4":
                    otp = get_otp_fish(mail_session, email, auth_key_fish)
                else:
                    otp = get_otp_10min(mail_session)

                if not otp:
                    print(f"{Y}[!] Dang thu lai..{W}")
                    driver.refresh()
                    time.sleep(5)
                    if mail_source == "2":
                        otp = get_otp_10p(mail_session, email)
                    else:
                        otp = get_otp_10min(mail_session)
            else:
                otp = input(f"{Y}>> Nhap ma cho {email}: {W}").strip()

            if not otp:
                raise Exception("Khong lay duoc OTP")

            code_el = driver.find_element(By.NAME, "code")
            send_keys_slowly(code_el, otp)
            print(f"{G}[OTP] Da nhap ma: {C}{otp}{W}")

            code_el.send_keys(Keys.ENTER)

            try:
                driver.find_element(By.XPATH, "//button[@type='submit']").click()
            except Exception:
                pass  # Nút có thể không tồn tại sau khi nhấn Enter
            print(f"{Y}[WAIT] Dang gui ma xac nhan...{W}")
            time.sleep(4)

        except Exception as e_code:
            print(f"{R}[!] Loi xac thuc: {e_code}{W}")
            print(f"{R}[!] URL hien tai: {driver.current_url}{W}")
            shutil.rmtree(my_p_path, ignore_errors=True)
            return

        driver.get("https://m.facebook.com/")
        time.sleep(6)
        final_url = driver.current_url
        cookies = driver.get_cookies()
        ck_dict = {c['name']: c['value'] for c in cookies}
        ck_str = "; ".join([f"{k}={v}" for k, v in ck_dict.items()])

        if 'c_user' in ck_dict:
            uid = ck_dict['c_user']
            status = f"{G}THANH CONG{W}"
            with open(f"{SAVE_DIR}/fb_live.txt", "a", encoding="utf-8") as f:
                f.write(f"{uid}|{pw}|{email}|{ck_str}|{proxy_str}\n")
        else:
            status = f"{R}CHECKPOINT{W}"
            shutil.rmtree(my_p_path, ignore_errors=True)

        print(f"\n{MG}{'+'*78}")
        print(f" {MY}[><] Ten       : {W}{full_name}")
        print(f" {MY}[><] UID       : {W}{uid}")
        print(f" {MY}[><] Pass      : {W}{pw}")
        print(f" {MY}[><] Cookies   : {G}{ck_str[:80]}...{W}")
        print(f" {MY}[><] Trang thai: {status}")
        print(f" {MY}[><] URL       : {W}{final_url}")
        print(f"{MG}{'+'*78}{W}\n")

    except Exception as e:
        print(f"{R}[LOI HE THONG]: {e}{W}")
        traceback.print_exc()
        shutil.rmtree(my_p_path, ignore_errors=True)
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

# ========== MENU CHÍNH ==========
def main():
    # === HIỂN THỊ THÔNG TIN MÔI TRƯỜNG ===
    clean_screen()
    
    if IS_TERMUX:
        print(f"{G}[INFO] Dang chay tren Termux/Android{W}")
    elif IS_LINUX:
        print(f"{G}[INFO] Dang chay tren Linux{W}")
    else:
        print(f"{G}[INFO] Dang chay tren Windows{W}")
    
    print()
    
    # === HỎI SETUP ===
    ans = input(f"{Y}[?] Ban co muon chay SETUP (cai thu vien)? (c/k): {W}").strip().lower()
    if ans in ['c', 'y', 'co', 'yes']:
        if IS_TERMUX:
            run_termux_setup()
        else:
            run_desktop_setup()
    
    # === IMPORT THƯ VIỆN ===
    print(f"\n{Y}[...] Dang kiem tra thu vien...{W}")
    if not safe_import():
        print(f"\n{R}[!] Khong the import thu vien can thiet.{W}")
        print(f"{Y}    Chay lai va chon 'c' de setup tu dong.{W}")
        input(f"{Y}Nhan Enter de thoat...{W}")
        sys.exit(1)
    print(f"{G}[OK] Tat ca thu vien da san sang!{W}\n")
    time.sleep(1)
    
    # === MENU LOOP ===
    while True:
        clean_screen()
        print(f"{C} s. Chay Setup (cai thu vien)")
        print(f"{G} 1. Reg Mail Thu Cong")
        print(f"{G} 2. Reg Mail Tu Dong")
        print(f"{R} 0. Thoat{W}")
        print()

        choice = input(f"{Y}[?] Nhap lua chon: {W}").strip()
        if choice == '0': 
            print(f"{G}Tam biet!{W}")
            break
        
        if choice.lower() == 's':
            if IS_TERMUX:
                run_termux_setup()
            else:
                run_desktop_setup()
            # Re-import sau khi setup
            safe_import()
            continue

        if choice == '1':
            proxy_input = input(f"{G}[?] Nhap Proxy (Enter = khong dung): {W}").strip()
            em_in = input(f"{G}[?] Nhap Email: {W}").strip()
            if em_in:
                run_one_account(proxy_input, mode="manual", email_manual=em_in, mail_source="1")
            else:
                print(f"{R}[!] Chua nhap email!{W}")
            input(f"\n{Y}Nhan Enter de tiep tuc...{W}")

        elif choice == '2':
            print(f"\n{C}--- CHON NGUON EMAIL ---{W}")
            print(f"{G} 1. 10minutemail.net")
            print(f"{G} 2. mail10p.com{W}")
            print(f"{G} 3. free.priyo.email{W}")
            print(f"{G} 4. tempmail.fish{W}")
            m_source = input(f"{Y}[?] Nhap lua chon: {W}").strip()

            proxy_list_str = input(f"{G}[?] Nhap Proxy (cach nhau boi | , Enter = khong): {W}").strip()
            proxies = [p.strip() for p in proxy_list_str.split('|')] if proxy_list_str else [None]

            try:
                num_acc = int(input(f"{G}[?] So luong acc muon tao: {W}").strip())
            except:
                num_acc = 1

            print(f"\n{Y}>>> Bat dau tao {num_acc} tai khoan...{W}")

            for i in range(num_acc):
                print(f"\n{B}[START] Dang tao tai khoan {i+1}/{num_acc}{W}")
                current_proxy = proxies[i % len(proxies)]
                run_one_account(current_proxy, mode="auto", mail_source=m_source)
                if i < num_acc - 1:
                    print(f"{Y}[...] Doi 10 giay truoc khi tao tiep...{W}")
                    time.sleep(10)

            input(f"\n{Y}Hoan Thanh! Nhan Enter de quay lai Menu...{W}")

if __name__ == "__main__":
    main()