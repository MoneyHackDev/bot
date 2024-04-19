import threading
import requests
import random
import json
import ctypes
import time
import base64
import sys
import re
import os
from prettytable import PrettyTable
from colorama import init, Fore
from urllib.parse import urlparse, unquote
from string import ascii_letters, digits

class Zefoy:
    def __init__(self):
        self.base_url = 'https://zefoy.com/'
        self.proxy = {'http': '38.162.18.39:3128'}  # Add your proxy URL here
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.proxies.update(self.proxy)  # Update session with proxy
        self.captcha_1 = None
        self.captcha_ = {}
        self.service = 'Views'
        self.video_key = None
        self.services = {}
        self.services_ids = {}
        self.services_status = {}
        self.url = 'None'
        self.text = 'Bot'

        # Check if config file exists, create one with default settings if not
        if not os.path.exists('config.json'):
            default_config = {
                'url': 'https://www.tiktok.com/@accshop.pw/video/7357825396718538027',
                'service': 'Views'
            }
            with open('config.json', 'w', encoding='utf-8', errors='ignore') as f:
                json.dump(default_config, f, indent=4)

        # Load config settings
        self.load_config()

    def load_config(self):
        try:
            with open('config.json', 'r', encoding='utf-8', errors='ignore') as f:
                config = json.load(f)
                self.url = config.get('url', 'https://www.tiktok.com/@accshop.pw/video/7357825396718538027')
                self.service = config.get('service', 'Views')
                self.update_config()
        except Exception as e:
            print(f"Error loading config: {e}")

    def update_config(self):
        try:
            with open('config.json', 'w', encoding='utf-8', errors='ignore') as f:
                config = {
                    'url': self.url,
                    'service': self.service
                }
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error updating config: {e}")

    def get_captcha(self):
        if os.path.exists('session'):
            self.session.cookies.set("PHPSESSID", open('session', encoding='utf-8').read(), domain='zefoy.com')
        request = self.session.get(self.base_url, headers=self.headers)
        if 'Enter Video URL' in request.text:
            self.video_key = request.text.split('" placeholder="Enter Video URL"')[0].split('name="')[-1]
            return True

        try:
            for x in re.findall(r'<input type="hidden" name="(.*)" value="(.*)">', request.text):
                self.captcha_[x[0]] = x[1]

            self.captcha_1 = request.text.split('type="text" name="')[1].split('" oninput="this.value=this.value.toLowerCase()"')[0]
            captcha_url = request.text.split('<img src="')[1].split('" onerror="imgOnError()" class="')[0]
            request = self.session.get(f"{self.base_url}{captcha_url}", headers=self.headers)
            open('captcha.png', 'wb').write(request.content)
            print('Solving captcha..')
            return False
        except Exception as e:
            print(f"Can't get captcha: {e}")
            time.sleep(2)
            self.get_captcha()

    def send_captcha(self, new_session=False):
        if new_session:
            self.session = requests.Session()
            os.remove('session')
            time.sleep(2)
        if self.get_captcha():
            print('Connected to session')
            return (True, 'The session already exists')
        captcha_solve = self.solve_captcha('captcha.png')[1]
        self.captcha_[self.captcha_1] = captcha_solve
        request = self.session.post(self.base_url, headers=self.headers, data=self.captcha_)

        if 'Enter Video URL' in request.text:
            print('Session was created')
            open('session', 'w', encoding='utf-8').write(self.session.cookies.get('PHPSESSID'))
            self.video_key = request.text.split('" placeholder="Enter Video URL"')[0].split('name="')[-1]
            return (True, captcha_solve)
        else:
            return (False, captcha_solve)

    def solve_captcha(self, path_to_file=None, b64=None, delete_tag=['\n', '\r']):
        if path_to_file:
            task = path_to_file
        else:
            open('temp.png', 'wb').write(base64.b64decode(b64))
            task = 'temp.png'
        
        # API for solving captcha
        request = self.session.post('https://api.ocr.space/parse/image?K87899142388957', headers={'apikey': 'K87899142388957'}, files={'task': open(task, 'rb')}).json()
        solved_text = request['ParsedResults'][0]['ParsedText']
        for x in delete_tag:
            solved_text = solved_text.replace(x, '')
        return (True, solved_text)

    def get_status_services(self):
        request = self.session.get(self.base_url, headers=self.headers).text
        for x in re.findall(r'<h5 class="card-title">.+</h5>\n.+\n.+', request):
            self.services[x.split('<h5 class="card-title">')[1].split('<')[0].strip()] = x.split('d-sm-inline-block">')[1].split('</small>')[0].strip()
        for x in re.findall(r'<h5 class="card-title mb-3">.+</h5>\n<form action=".+">', request):
            self.services_ids[x.split('title mb-3">')[1].split('<')[0].strip()] = x.split('<form action="')[1].split('">')[0].strip()
        for x in re.findall(r'<h5 class="card-title">.+</h5>\n.+<button .+', request):
            self.services_status[x.split('<h5 class="card-title">')[1].split('<')[0].strip()] = False if 'disabled class' in x else True
        return (self.services, self.services_status)

    def get_table(self, i=1):
        table = PrettyTable(field_names=["ID", "Services", "Status"], title="Status Services", header_style="upper", border=True)
        while True:
            if len(self.get_status_services()[0]) > 1:
                break
            else:
                print('Cannot get services, retrying...')
                self.send_captcha()
                time.sleep(2)
        for service in self.services:
            table.add_row([f"{Fore.CYAN}{i}{Fore.RESET}", service, f"{Fore.GREEN if 'ago updated' in self.services[service] else Fore.RED}{self.services[service]}{Fore.RESET}"])
            i += 1
        table.title = f"{Fore.YELLOW}Total Online Services: {len([x for x in self.services_status if self.services_status[x]])}{Fore.RESET}"
        print(table)

    def find_video(self):
        if self.service is None:
            return (False, "You didn't choose the service")
        while True:
            if self.service not in self.services_ids:
                self.get_status_services()
                time.sleep(1)
            request = self.session.post(f'{self.base_url}{self.services_ids[self.service]}', headers={'content-type': 'multipart/form-data; boundary=----WebKitFormBoundary0nU8PjANC8BhQgjZ', 'user-agent': self.headers['user-agent'], 'origin': 'https://zefoy.com'}, data=f'------WebKitFormBoundary0nU8PjANC8BhQgjZ\r\nContent-Disposition: form-data; name="{self.video_key}"\r\n\r\n{self.url}\r\n------WebKitFormBoundary0nU8PjANC8BhQgjZ--\r\n')
            try:
                self.video_info = base64.b64decode(unquote(request.text.encode()[::-1])).decode()
            except:
                time.sleep(3)
                continue
            if 'Session expired. Please re-login' in self.video_info:
                print('Session expired. Relogging...')
                self.send_captcha()
                return
            elif 'service is currently not working' in self.video_info:
                return (True, 'Service is currently not working, try again later. | You can change it in config.')
            elif """onsubmit="showHideElements""" in self.video_info:
                self.video_info = [self.video_info.split('" name="')[1].split('"')[0], self.video_info.split('value="')[1].split('"')[0]]
                return (True, request.text)
            elif 'Checking Timer...' in self.video_info:
                try:
                    t = int(re.findall(r'ltm=(\d*);', self.video_info)[0])
                except:
                    return (False,)
                if t == 0:
                    self.find_video()
                elif t >= 1000:
                    print('Your IP was banned')
                print(f'Time to next use: {t}')
                _ = time.time()
                while time.time() - 2 < _ + t:
                    time.sleep(1)
                continue
            elif 'Too many requests. Please slow' in self.video_info:
                time.sleep(3)
            else:
                print(self.video_info)

    def use_service(self):
        if self.find_video()[0] is False:
            return False
        self.token = "".join(random.choices(ascii_letters + digits, k=16))
        request = self.session.post(f'{self.base_url}{self.services_ids[self.service]}', headers={'content-type': f'multipart/form-data; boundary=----WebKitFormBoundary{self.token}', 'user-agent': self.headers['user-agent'], 'origin': 'https://zefoy.com'}, data=f'------WebKitFormBoundary{self.token}\r\nContent-Disposition: form-data; name="{self.video_info[0]}"\r\n\r\n{self.video_info[1]}\r\n------WebKitFormBoundary{self.token}--\r\n')
        try:
            res = base64.b64decode(unquote(request.text.encode()[::-1])).decode()
        except:
            time.sleep(3)
            return ""
        if 'Session expired. Please re-login' in res:
            print('Session expired. Relogging...')
            self.send_captcha()
            return ""
        elif 'Too many requests. Please slow' in res:
            time.sleep(3)
        elif 'service is currently not working' in res:
            return ('Service is currently not working, try again later. | You can change it in config.')
        else:
            print(res.split("sans-serif;text-align:center;color:green;'>")[1].split("</")[0])

    def get_video_info(self):
        request = self.session.get(f'https://tiktok.livecounts.io/video/stats/{urlparse(self.url).path.rpartition("/")[2]}', headers={'authority': 'tiktok.livecounts.io', 'origin': 'https://livecounts.io', 'user-agent': self.headers['user-agent']}).json()
        if 'viewCount' in request:
            return request
        else:
            return {'viewCount': 0, 'likeCount': 0, 'commentCount': 0, 'shareCount': 0}

    def get_video_id(self, url_=None, set_url=True):
        if url_ is None:
            url_ = self.url
        if url_[-1] == '/':
            url_ = url_[:-1]
        url = urlparse(url_).path.rpartition('/')[2]
        if url.isdigit():
            self.url = url_
            return url_
        request = requests.get(f'https://api.tokcount.com/?type=videoID&username=https://vm.tiktok.com/{url}', headers={'origin': 'https://tokcount.com', 'authority': 'api.tokcount.com', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'})
        if request.text == '':
            print('Invalid URL | Replace in config')
            return False
        else:
            json_ = request.json()
        if 'author' not in json_:
            print(f'{self.url}| invalid URL | Replace in config')
            return False
        if set_url:
            self.url = f'https://www.tiktok.com/@{json_["author"]}/video/{json_["id"]}'
            print(f'Formatted video url --> {self.url}')
        return request.text

    def check_config(self):
        while True:
            try:
                last_url = self.url
                self.load_config()
                if last_url != self.url:
                    self.get_video_id()
                    self.update_config()
            except Exception as e:
                print(e)
            time.sleep(4)

    def update_name(self):
        while True:
            try:
                ctypes.windll.kernel32.SetConsoleTitleA(self.text.encode())
                video_info = self.get_video_info()
                self.text = f"INFO | Views: {video_info['viewCount']} | Likes: {video_info['likeCount']} | Comments: {video_info['commentCount']} | Shares: {video_info['shareCount']}"
            except:
                pass
            time.sleep(5)

# Create and start the Zefoy instance
Z = Zefoy()

# Start threads for continuous operations
threading.Thread(target=Z.check_config).start()
threading.Thread(target=Z.update_name).start()

# Perform initial actions
Z.send_captcha()
Z.get_table()

# Continuous operation loop
while True:
    try:
        if 'Service is currently not working, try again later' in str(Z.use_service()):
            print('Service is currently not working, try again later. | You can change it in config.')
            time.sleep(5)
    except Exception as e:
        print(f'Critical ERROR | retrying in 10 seconds. ||| {e}')
        time.sleep(10)
