#%%
from time import sleep
import pyrootutils
DIR_ROOT = pyrootutils.setup_root(__file__)

import sys
import math
from pathlib import Path

sys.path.append(str(Path(".").parent.absolute()))

from datetime import datetime, timedelta
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from src.modules.publisher.trend_m import TMPublisher, TMDriver, TMUserInfo


def init_driver():
    tm_driver = TMDriver(
        headless= False,
        user_info = TMUserInfo(
            email    = "paulracooni@gmail.com",
            password = "paul"))
    try:
        if not tm_driver.check_logined():
            tm_driver.login()
    except Exception as e:
        print(e)
        try:
            tm_driver.driver.close()
        except:
            pass
    
    return tm_driver.driver

def goto_admin_post(driver, keyword="트렌드M", page=1, board_code=""):
    url = "https://trend-m.com/admin/contents/post"
    driver.get(f"{url}?"
               f"keyword={keyword}&"
               f"page={page}&"
               f"board_code={board_code}")
    
def get_items(driver):
    
    items = []
    for content in driver.find_elements(By.CLASS_NAME, "content"):
        
        post_id = content.get_attribute("id").replace("post_item_", "")
        board_name = content.find_element(By.CLASS_NAME, "based").text
        date = content.find_element(By.CLASS_NAME, "date").get_attribute("title")
        date = datetime.strptime(date, "%Y-%m-%d %H:%M")
        check_box = content.find_element(By.TAG_NAME, "label")    
        author = content.find_element(By.CLASS_NAME, "author").text
        items.append(dict(
            post_id    = post_id,
            board_name = board_name,
            date       = date,
            author     = author,
            check_box = check_box,))

    return items

def filter_items(items, overdate=3, author='트렌드M'):
    
    items = filter(
        lambda item: "테스트" in item['board_name'], items)
    
    items = filter(
        lambda item: author in item['author'], items)
    
    today    = datetime.now()
    overdate = timedelta(days=overdate)
    items    = filter(
        lambda item: today - item["date"] > overdate, items)

    return list(items)

def click_items_all(items):
    for i in items:
        i['check_box'].click()

def ignore_exceptions(exceptions):
    def decorator(function):
        def wrapper(*args, **kwargs):
            try:
                result = function(*args, **kwargs)
            except exceptions:
                return None
            return result
        return wrapper
    return decorator

@ignore_exceptions(TimeoutException)
def uncheck_all_items(driver):

    WebDriverWait(driver, 1).until(
        EC.visibility_of_element_located((By.ID, "dLabel"))).click()

    WebDriverWait(driver, 1).until(
        EC.visibility_of_element_located((
            By.XPATH,
            "//*[@id='select_header']/div/div[1]/ul/li/div[2]/div/ul/li[2]/a"))).click()


@ignore_exceptions(TimeoutException)
def delete_checked_items(driver):
    WebDriverWait(driver, 1).until(
            EC.visibility_of_element_located((
                By.XPATH,
                "//*[@id='select_header']/div/div[2]/ul/li[2]/div/a"))).click()

    WebDriverWait(driver, 1).until(
            EC.visibility_of_element_located((
                By.XPATH,
                "//*[@id='cocoaModal']/div/div/div[3]/button[2]"))).click()

#%%
driver = init_driver()

#%%
board_codes = {
    '아이디어_마케팅 (테스트)': 'b20230731b5afa2fdc85b9',
    '아이디어_브랜딩 (테스트)': 'b20230731f2b89979bcb12',
    '아이디어_라이프스타일 (테스트)': 'b20230731b2cf9374bb852',
    '아이디어_비즈니스 (테스트)': 'b202307313c1f31bc630ec',
    '아이디어_테크 (테스트)': 'b2023073183946747fd582',
    '아이디어_소비자 (테스트)': 'b202307313165ed7e36ec6',
    '아이디어_콘텐츠 (테스트)': 'b20230731882b63588c5b0',
    '아이디어_디자인 (테스트)': 'b20230731f588ec39adfd9',
    '아이디어_컬처 (테스트)': 'b20230731464316e0e6d7d',
    '아이디어_ESG (테스트)': 'b20230731e1c0c1df59371',
    '아이디어_제너레이션 (테스트)': 'b2023073174608e5589c93',
    '아이디어_이코노미 (테스트)': 'b202307318997586adb159',
}  

cnt_post_per_page = 20
                                    

for board_name, board_code in board_codes.items():
    
    # Init Action
    goto_admin_post(driver,
        keyword    = "트렌드M",
        page       = 1,
        board_code = board_code)


    cnt_total_post = int(driver.find_element(By.ID, "comment_count").text)
    cnt_total_page = math.ceil(cnt_total_post / cnt_post_per_page)

    # Start Delete task
    while cnt_total_post:
        
        # Page 이동
        goto_admin_post(driver,
            keyword    = "트렌드M",
            page       = cnt_total_page,
            board_code = board_code)

        # 아이템 선택
        items = get_items(driver)
        items = filter_items(items, overdate=3)
        
        # 선택된 아이템이 없을 경우 종료
        if not items: break

        # 선택된 아이템이 있을 경우
        # 기존 선택된 아이템 모두 초기화 후
        uncheck_all_items(driver)
        
        # 선택 아이템 선택 후
        click_items_all(items)
        
        # 선택 아이템 삭제
        delete_checked_items(driver)

        # 삭제 후, 현재 게시글 수, 전체 피이지 수 재 계산
        cnt_total_post = int(driver.find_element(By.ID, "comment_count").text)
        cnt_total_page = math.ceil(cnt_total_post / cnt_post_per_page)
        
    