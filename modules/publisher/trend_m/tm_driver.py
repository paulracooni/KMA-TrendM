import re
import requests
from pathlib import Path
from urllib.parse import urlparse, urljoin

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import chromedriver_autoinstaller

from utils import Env

PATH_TEMPLATE = Path(__file__).parent / "template" / "basic.html"

class TMDriver:
    HOST = 'https://trend-m.com'

    PAGES = {
        "MARKETING" : "idea_marketing",
        "BRANDING"  : "idea_branding",
        "LIFESTYLE" : "idea_lifestyle",
        "BUSINESS"  : "idea_business",
        "TECH"      : "idea_tech",
        "CONSUMER"  : "idea_consumer",
        "CONTENTS"  : "idea_contents",
        "DESIGN"    : "idea_design",
        "CULTURE"   : "idea_culture",
        "ESG"       : "idea_esg",
        "GENERATION": "idea_generation",
        "ECONOMY"   : "idea_economy",    }

    TEMPLATE = PATH_TEMPLATE.open("r", encoding="UTF-8").read()

    def __init__(self, user_info, headless=True, timeout=10):
        # Init driver
        options=self.__init_options(headless)
        self.driver=webdriver.Remote(
            command_executor = Env.get('SELENIUM_EXECUTOR'),
            options          = options, )
        self.driver.maximize_window()
        # members
        self.timeout=timeout
        self.user_info = user_info

    def __init_options(self, headless):
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--ignore-ssl-errors=yes")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--window-size=1920,1080")
        options.add_argument('--allow-running-insecure-content')
        # options.add_argument('--remote-debugging-port=9222')
        
        if headless:
            options.add_argument('--headless')
        return options

#region login
    def check_logined(self):
        self.driver.get(self.HOST)
        slctr_btn_logout = r"#w202111123ebc62b3d2c4a > div > div > div > div:nth-child(2) > a"
        btn_logout = self.__get_btn(slctr_btn_logout)
        return {'Logout':True}.get(btn_logout.text, False)

    def login(self):
        self.driver.get(self.HOST)
        # Pop-up Login modal
        self.__get_btn(
            slctr=r"#w202111123ebc62b3d2c4a > div > div > div > div:nth-child(1) > a").click()
        # Input Email
        self.__input_form(
            slctr=r"#cocoaModal > div > div > article > form > div.input_block > div:nth-child(1) > input[type=text]",
            data=self.user_info.email)
        # Input Password
        self.__input_form(
            slctr=r"#cocoaModal > div > div > article > form > div.input_block > div.input_form.brt > input[type=password]",
            data=self.user_info.password)
        # Submit login
        self.__get_btn(
            slctr=r"#cocoaModal > div > div > article > form > p > button").click()

        # Wait until logined
        self.driver.get(self.HOST)

    def __input_form(self, slctr, data):
        form = self.__get_form(slctr)
        form.clear()
        form.send_keys(data)
        self.__wait_until_sended(form, data)
        return form
#endregion

#region posting
    def goto_page(self, section):
        section = section.upper()
        assert section in self.PAGES.keys(), f"No section - {section}"
        
        self.driver.get(urljoin(self.HOST, self.PAGES[section]))
        
        self.__get_btn(slctr=r".btn-block-right > a").click()

    def _make_token(self):
        session = requests.Session()
        for cookie in self.driver.get_cookies():
            session.cookies.set(cookie['name'], cookie['value'])

        response = session.post(
            "https://trend-m.com/ajax/make_tokens.cm",
            headers={
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                "user-agent"  : self.driver.execute_script('return navigator.userAgent'),
                'referer'     : self.driver.current_url
            },
            data = {
                'expire': 86_400,
                'count' : 1
            }
        )

        if response.status_code == 200:
            token = response.json()['tokens'][0]['token']
            token_key = response.json()['tokens'][0]['token_key']
        
        else:
            raise RuntimeError(
                f"TMDriver._make_token error - status_code={response.status_code}")
        
        return token, token_key
    
    def _write_post(self, subject, body_html, image_url, token, token_key):
        session = requests.Session()
        for cookie in self.driver.get_cookies():
            session.cookies.set(cookie['name'], cookie['value'])

        params_url = dict(map(
            lambda q: q.split("="),
            urlparse(self.driver.current_url).query.split("&")))

        response = session.post(
            "https://trend-m.com/backpg/post_add.cm",
            headers={
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                "user-agent"  : self.driver.execute_script('return navigator.userAgent'),
                'referer'     : self.driver.current_url
            },
            data = {
                'idx'            : 0,
                'menu_url'       : "/idea_marketing/", # TODO: Categorization
                'back_url'       : "",
                "back_page_num"  : "",
                "board_code"     : params_url['board'],
                "plain_body"     : "",
                "is_editor"      : "Y",
                "represent_img"  : image_url,
                "img"            : "",
                "img_tmp_no"     : "",
                "is_notice"      : "no",
                "category_type"  : 0,
                "write_token"    : token,
                "write_token_key": token_key,
                "is_secret_post" : "no",
                "subject"        : subject,
                "body"           : body_html
            }
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"TMDriver._make_token error - status_code={response.status_code}")
        
        pattern = r"\/idea_marketing\/\?bmode=view&idx=([0-9]+)&back_url=&t=board&page="
        code = re.findall(pattern, response.text)[0]

        return urljoin(
            self.HOST, 
            f"/idea_marketing/?bmode=view&idx={code}&back_url=&t=board&page=")
#endregion

#post-deletion
    def delte_all_post(self, name, verbose=True):

        n_post = 9999
        while n_post:

            self.driver.get(
                f"https://trend-m.com/admin/contents/post?keyword={name}")
            
            n_post = self.__get_form("#comment_count").text
            if not n_post.isnumeric() or not int(n_post):
                break
            n_post = int(n_post)
            if verbose: print(f"remain post - {n_post}")

            # Radio btn
            self.__get_btn("li.check > div > label").click()
            # Delete btn
            self.__get_btn("#select_header > div > div.headerbar-right > ul > li:nth-child(2) > div > a").click()
            # Submit btn
            self.__get_btn("#cocoaModal > div > div > div.modal-footer > button.btn.btn-primary.btn-flat._submit").click()


#region utils
    def __get_btn(self, slctr):
        return WebDriverWait(self.driver, self.timeout).until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR, slctr )))

    def __get_form(self, slctr):
        return WebDriverWait(self.driver, self.timeout).until(
            EC.visibility_of_element_located((
                By.CSS_SELECTOR, slctr)))
    
    def __wait_until_sended(self, form, value):
        WebDriverWait(self.driver, self.timeout).until(
            lambda browser: {value:True}.get(
                form.get_attribute('value'), False))

#endregion