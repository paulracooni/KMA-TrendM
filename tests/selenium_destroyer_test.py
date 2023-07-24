import pyrootutils
DIR_ROOT = pyrootutils.setup_root(__file__)

from models import NewsDB, TrendMSummary
from modules.publisher.trend_m import TMPublisher, TMDriver, TMUserInfo


def delete_all_post():
    
    driver = TMDriver(
        user_info = TMUserInfo(
            email    = "paulracooni@gmail.com",
            password = "paul"))
    try:
        if not driver.check_logined():
            driver.login()

        driver.delte_all_post("김명석", verbose=True)
        driver.driver.close()
    except Exception as e:
        try:
            driver.driver.close()
        except:
            pass
        delete_all_post()

def reset_all_trend_m_summary():
    with NewsDB._meta.database.atomic(): 

        for summary in TrendMSummary.select():
            summary.published     = False
            summary.published_url = None
            summary.save()

def post_all_trend_m_summary():
    publisher = TMPublisher(user_info = TMUserInfo(
            email    = "paulracooni@gmail.com",
            password = "paul"))
    publisher([summary.id for summary in TrendMSummary.select()])


if __name__ == '__main__':
    print("Start delete_all_post")
    delete_all_post()
