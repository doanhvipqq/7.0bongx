import random, string, time, os, shutil, sys, requests
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import urllib3
import re
import traceback
from fake_useragent import UserAgent
import logging
logging.getLogger('fake-useragent').setLevel(logging.ERROR)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
try:
    from seleniumwire import webdriver 
    from selenium_stealth import stealth
except ImportError:
    print(f"\033[31m[!] Thiếu thư viện. Hãy chạy:\n pip install selenium-wire blinker==1.7.0 setuptools requests selenium-stealth fake-useragent\n Nếu dùng Termux/Android, hãy chạy thêm: pkg install chromium chromedriver\033[0m")
    sys.exit()

# HACK FIX CHO TERMUX: Bypass Selenium Manager lỗi binary
try:
    if os.path.exists("/data/data/com.termux/files/usr/bin/chromedriver"):
        from selenium.webdriver.common import selenium_manager
        # Override hàm tìm driver để KHÔNG CHẠY binary selenium-manager
        def dummy_location(self, options):
            return "/data/data/com.termux/files/usr/bin/chromedriver"
        
        selenium_manager.SeleniumManager.driver_location = dummy_location
except:
    pass

# MÀU
R = '\033[31m'; G = '\033[32m'; Y = '\033[33m'; B = '\033[34m'
C = '\033[36m'; W = '\033[0m'; MG = '\033[1;32m'; MY = '\033[1;33m'


BASE_PROFILE_DIR = os.path.join(os.getcwd(), "fb_profiles_hidden")
SAVE_DIR = os.path.join(os.getcwd(), "reg_fb_pro")

for d in [BASE_PROFILE_DIR, SAVE_DIR]:
    if not os.path.exists(d): os.makedirs(d)

#TÊN
HOS = ["Nguyễn", "Trần", "Lê", "Phạm", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương"]
TEN_NAM = ["Tuấn", "Dũng", "Hùng", "Nam", "Khánh", "Minh", "Đức", "Trung", "Hiếu", "Hoàng", "Long", "Quân"]
TEN_NU = ["Lan", "Huệ", "Mai", "Trang", "Thảo", "Linh", "Hương", "Hằng", "Thu", "Ngọc", "Vy", "Hân"]

TOKEN_TEMPMAIL = "7446|gUV1YA7SRO7JOv4QbBzYMWRKYRMudibUgfgYCHHz0cdbc4be"
API_KEY_PRIYO = "7jkmE5NM2VS6GqJ9pzlI"
API_KEY_10P = "pdZWgJngWyba9BH2SzOn8wlmNjifV1f"
API_BASE_10P = "https://mail10p.com/api"

def clean_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{MG}======================================================")
    print("             TOOL REG FB")
    print(f"======================================================{W}")

def get_current_ip(proxy_config):
    try:
        proxies = proxy_config['proxy'] if proxy_config and 'proxy' in proxy_config else None
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.7632.45 Safari/537.36'
        }
        
        response = requests.get(
            'http://api.ipify.org?format=json', 
            proxies=proxies, 
            timeout=20, 
            headers=headers,
            verify=False
        )
        return response.json()['ip']
    except:
        try:
            
            response = requests.get('http://ifconfig.me/ip', proxies=proxies, timeout=15, verify=False)
            return response.text.strip()
        except:
            return "Lỗi Proxy/Timeout"


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

def get_mail_fish(session):
    url = 'https://api.tempmail.fish/emails/new-email'
    try:
        res = session.post(url, timeout=15, verify=False)
        if res.status_code == 200:
            data = res.json()
            email = data.get('email')
            auth_key = data.get('authKey') # Key này dùng để đọc thư
            
            if email and auth_key:
                print(f"{G}[FISH-MAIL] Đã tạo: {C}{email}{W}")
                return email, auth_key
    except Exception as e:
        print(f"{R}[!] Lỗi tạo mail Fish: {e}{W}")
    return None, None
    
def get_otp_fish(session, email_address, auth_key):
    print(f"{Y}[WAIT] Đang đợi OTP từ tempmail.fish...{W}")
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
                        print(f"{G}[OTP] Mã: {C}{otp}{W}")
                        return otp
            time.sleep(7)
            print(f"{Y}[...] Đang quét hòm thư lần {i+1}/15...{W}")
        except:
            pass
    return None

def get_mail_priyo(session):
    try:
        url_domain = f"https://free.priyo.email/api/domains/{API_KEY_PRIYO}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = session.get(url_domain, headers=headers, timeout=15, verify=False)
        
        if response.status_code != 200:
            print(f"{R}[!] Priyo API lỗi: {response.status_code}{W}")
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
        print(f"{R}[!] Lỗi Priyo: {e}{W}")
    return None
    
def get_otp_priyo(session, email):
    print(f"{Y}[WAIT] Đang đợi mã {email}...{W}")
    for i in range(20):
        try:
            url = f"https://free.priyo.email/api/messages/{email}/{API_KEY_PRIYO}"
            messages = session.get(url, timeout=10, verify=False).json()
            
            if isinstance(messages, list):
                for msg in messages:
                    subject = msg.get('subject', '')
                    if any(x in subject.lower() for x in ["fb-", "facebook", "mã"]):
                        otp = "".join(re.findall(r'\d+', subject))
                        if len(otp) >= 5:
                            print(f"{G}[OTP] mã: {C}{otp[:6]}{W}")
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
                print(f"{G}[MAIL10P] Đã tạo Email: {C}{email}{W}")
                return email
    except: pass
    return None

def get_otp_10p(session, email):
    print(f"{Y}[WAIT] Đang đợi mã {email}...{W}")
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
                        if any(x in subject for x in ["FB-", "mã xác nhận", "Facebook"]):
                            otp = "".join(filter(str.isdigit, subject))
                            if len(otp) >= 5:
                                print(f"{G}[OTP] Mã: {C}{otp[:5]}{W}")
                                return otp[:5]
            print(f"{Y}[...] Đang load lại hòm thư ({int(time.time() - start_time)}s)...{W}")
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
                print(f"{G}[EMAIL] Đã lấy được email: {C}{email}{W}")
                return email
            else:
                print(f"{Y}[...] {email}. Đang đổi... ({i+1}){W}")
                time.sleep(2)
        except: continue
    return None

def get_otp_10min(session):
    """Quét OTP từ API 10minutemail.net"""
    print(f"{Y}[WAIT] Đang lấy mã...{W}")
    url_api = "https://10minutemail.net/address.api.php"
    for i in range(15): 
        try:
            time.sleep(10)
            res = session.get(url_api, timeout=15, verify=False).json()
            mail_list = res.get('mail_list', [])
            for mail in mail_list:
                subject = mail.get('subject', '')
                if "FB-" in subject or "mã xác nhận" in subject:
                    otp = "".join(filter(str.isdigit, subject))
                    if len(otp) >= 5: return otp[:5]
            print(f"{Y}[...] Đang đợi thư lần {i+1}/15...{W}")
        except: continue
    return None

def get_random_windows_ua():
    """Tạo User-Agent Windows động"""
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

def setup_driver(profile_path, proxy_config):
    """Cấu hình trình duyệt"""
    win_ua = get_random_windows_ua()
    print(f"{C}[DEVICE] FAKE UA: {W}{win_ua}")
    chrome_options = Options()
    # Tự động bật headless nếu chạy trên linux (Termux/Server) để tránh lỗi hiển thị
    if 'linux' in sys.platform or not os.environ.get('DISPLAY'):
        print(f"{Y}[DEVICE] Đang chạy chế độ Headless (Ẩn trình duyệt) cho Mobile/Linux{W}")
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-software-rasterizer")
        
    # Cấu hình đường dẫn Chromium/Driver cho Termux
    termux_chromium = "/data/data/com.termux/files/usr/bin/chromium-browser"
    termux_driver = "/data/data/com.termux/files/usr/bin/chromedriver"
    
    # Kiểm tra nếu đang chạy trên Termux (đường dẫn tồn tại)
    is_termux = os.path.exists("/data/data/com.termux")
    
    if is_termux and os.path.exists(termux_chromium):
        print(f"{Y}[DEVICE] Đang chạy trên Termux. Set đường dẫn Chromium...{W}")
        chrome_options.binary_location = termux_chromium
        
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"--user-data-dir={profile_path}")
    # chrome_options.add_argument("--window-size=1920,1080") # Bỏ qua để tiết kiệm tài nguyên trên mobile
    chrome_options.add_argument(f'--user-agent={win_ua}')
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Xử lý Service cho Chromedriver
    service = None
    
    # Ưu tiên 1: Termux driver path
    if is_termux and os.path.exists(termux_driver):
         print(f"{Y}[DEVICE] Set đường dẫn Chromedriver Termux...{W}")
         service = Service(executable_path=termux_driver)
    else:
        # Ưu tiên 2: Driver trong thư mục hiện tại
        local_driver = "chromedriver.exe" if os.name == 'nt' else "chromedriver"
        current_dir_driver = os.path.join(os.getcwd(), local_driver)
        
        if os.path.exists(current_dir_driver):
             service = Service(executable_path=current_dir_driver)
        # Ưu tiên 3: System PATH (shutil.which)
        elif shutil.which("chromedriver"):
             service = Service(executable_path=shutil.which("chromedriver"))
        else:
             # Cuối cùng: Để Selenium tự xử (có thể lỗi trên Termux)
             service = Service()

    try:
        driver = webdriver.Chrome(
            service=service, 
            options=chrome_options, 
            seleniumwire_options=proxy_config if proxy_config else {}
        )
    except Exception as e:
        print(f"{R}[ERROR] Lỗi khởi tạo Driver: {e}{W}")
        print(f"{Y}Hãy chắc chắn đã chạy: pkg install chromium chromedriver trong Termux{W}")
        raise e

    stealth(driver,
        user_agent=win_ua,
        languages=["vi-VN", "vi"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer=random.choice(["Intel(R) UHD Graphics 630", "Intel(R) Iris(R) Xe Graphics", "NVIDIA GeForce RTX 3060"]),
        fix_hairline=True,
    )
    return driver

def send_keys_slowly(element, text):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.2))

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
            print(f"{R}[!] Không lấy được mail. Bỏ qua.{W}")
            return 
    else:
        email = email_manual

    current_ip = get_current_ip(proxy_config)
    print(f"{Y}[IP] IP hiện tại: {C}{current_ip}{W}")
    
    temp_id = random.randint(1000, 9999)
    my_p_path = os.path.join(BASE_PROFILE_DIR, f"pro_{email.split('@')[0]}_{temp_id}")
    
    driver = setup_driver(my_p_path, proxy_config)
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
        print(f"{Y}[WAIT] Đã nhập tên...{W}")
        time.sleep(2)

        Select(wait.until(EC.presence_of_element_located((By.ID, "day")))).select_by_value(str(random.randint(1, 28)))
        Select(driver.find_element(By.ID, "month")).select_by_value(str(random.randint(1, 12)))
        Select(driver.find_element(By.ID, "year")).select_by_value(str(random.randint(1995, 2004)))
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        print(f"{Y}[WAIT] Đã nhập ngày sinh...{W}")
        time.sleep(2) 

        email_el = wait.until(EC.presence_of_element_located((By.NAME, "reg_email__")))
        send_keys_slowly(email_el, email)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        print(f"{Y}[WAIT] Đã nhập email...{W}")
        time.sleep(2)
        
        driver.find_element(By.XPATH, f"//input[@name='sex' and @value='{'2' if is_nam else '1'}']").click()
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        print(f"{Y}[WAIT] Đã nhập giới tính...{W}")
        time.sleep(2)
        
        pass_el = wait.until(EC.presence_of_element_located((By.NAME, "reg_passwd__")))
        send_keys_slowly(pass_el, pw)
        
        pass_el.send_keys(Keys.ENTER) 
        print(f"{Y}[WAIT] Đã gửi đăng ký{W}")
        
        time.sleep(1) 

        print(f"{Y}[WAIT] Đợi lúc...{W}")
        time.sleep(13) 

        try:
            if "checkpoint" in driver.current_url:
                print(f"{R}[!] Bị Checkpoint ngay lập tức. Bỏ acc!{W}")
                raise Exception("Checkpoint")

            wait_otp = WebDriverWait(driver, 45)
            wait_otp.until(EC.presence_of_element_located((By.NAME, "code")))
            print(f"{G}[OTP]Bắt đầu lấy OTP...{W}")
            
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
                    print(f"{Y}[!] Đang thử lại..{W}")
                    driver.refresh()
                    time.sleep(5)
                    otp = get_otp_10p(mail_session, email) if mail_source == "2" else get_otp_10min(mail_session)
            else:
                otp = input(f"{Y}👉 Nhập mã cho {email}: {W}").strip()
            
            if not otp:
                raise Exception("Không lấy được OTP")

            code_el = driver.find_element(By.NAME, "code")
            send_keys_slowly(code_el, otp)
            print(f"{G}[OTP] Đã nhập mã: {C}{otp}{W}") 
            
            code_el.send_keys(Keys.ENTER)
            
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
            print(f"{Y}[WAIT] Đang gửi mã xác nhận...{W}")
            time.sleep(4)

        except Exception as e_code:
            print(f"{R}[!] Lỗi xác thực: {e_code}{W}")
            print(f"{R}[!] URL hiện tại: {driver.current_url}{W}")
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
            status = f"{G}THÀNH CÔNG{W}"
            with open(f"{SAVE_DIR}/fb_live.txt", "a", encoding="utf-8") as f:
                f.write(f"{uid}|{pw}|{email}|{ck_str}|{proxy_str}\n")
        else:
            status = f"{R} CHECKPOINT{W}"
            shutil.rmtree(my_p_path, ignore_errors=True) # Xóa profile nếu die

        print(f"\n{MG}++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        print(f" {MY}[><] 👤 Tên       : {W}{full_name}")
        print(f" {MY}[><] 🪪 UID       : {W}{uid}")
        print(f" {MY}[><] 🔑 Pass      : {W}{pw}")
        print(f" {MY}[><] 🍪 Cookies   : {G}{ck_str}{W}")
        print(f" {MY}[><] 📌 Trạng thái: {status}")
        print(f" {MY}[><] 🔗 URL       : {W}{final_url}")
        print(f"{MG}++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++{W}\n")

    except Exception as e:
        print(f"{R}[LỖI HỆ THỐNG]: {e}. Đang hủy acc...{W}")
        shutil.rmtree(my_p_path, ignore_errors=True)
    finally:
        driver.quit()

def main():
    while True:
        clean_screen()
        print(f"{G} 1. Reg Mail Thủ Công")
        print(f"{G} 2. Reg Mail Tự Động")
        print(f"{R} 0. Thoát{W}")
        
        choice = input(f"{Y}[?] Nhập lựa chọn: {W}").strip()
        if choice == '0': break
        
        if choice == '1':
            proxy_input = input(f"{G}[?] Nhập Proxy: {W}").strip()
            em_in = input(f"{G}[?] Nhập Email:{W} ").strip()
            if em_in:
                run_one_account(proxy_input, mode="manual", email_manual=em_in, mail_source="1")
        
        elif choice == '2':
            print(f"\n{C}--- CHỌN NGUỒN EMAIL ---{W}")
            print(f"{G} 1. 10minutemail.net")
            print(f"{G} 2. mail10p.com{W}")
            print(f"{G} 3. free.priyo.email{W}")
            print(f"{G} 4. tempmail.fish{W}")
            m_source = input(f"{Y}[?] Nhập lựa chọn: {W}").strip()

            proxy_list_str = input(f"{G}[?] Nhập danh sách Proxy (cách nhau bởi | ): {W}").strip()
            proxies = [p.strip() for p in proxy_list_str.split('|')] if proxy_list_str else [None]
            
            try:
                num_acc = int(input(f"{G}[?] Nhập số lượng acc muốn tạo: {W}").strip())
            except:
                num_acc = 1
                
            print(f"{Y}>>> Bắt đầu tạo {num_acc} tài khoản...{W}")
            
            for i in range(num_acc):
                print(f"\n{B}[START] Đang tạo tài khoản {i+1}/{num_acc}{W}")
                current_proxy = proxies[i % len(proxies)]
                run_one_account(current_proxy, mode="auto", mail_source=m_source)
                time.sleep(10) 
            
            input(f"\n{Y}Hoàn Thành. Nhấn Enter để quay lại Menu...{W}")

if __name__ == "__main__":
    main()