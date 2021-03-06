import logging
import atexit
from typing import Tuple

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

logger = logging.getLogger()

options = Options()
options.add_argument("--headless")
options.add_argument('window-size=1920,1080')

driver = webdriver.Firefox(firefox_options=options)
    
def close_driver():
    driver.close()


atexit.register(close_driver)


def load_start_page():
    driver.get("https://odysseypa.traviscountytx.gov/JPPublicAccess/default.aspx")
    return driver


def load_search_page():
    start_page = load_start_page()
    try:
        element = WebDriverWait(start_page, 10).until(
            EC.presence_of_element_located(
                (By.LINK_TEXT, "Civil, Family & Probate Case Records")
            )
        )
    finally:
        element.click()
        return start_page
    return None


def query_case_id(case_id: str):
    search_page = load_search_page()
    try:
        case_radio_button = WebDriverWait(search_page, 10).until(
            EC.presence_of_element_located((By.ID, "Case"))
        )
        case_radio_button.click()
    except:
        logger.error(f"Could not click button to search for case {case_id}")
        return None

    try:
        search_box = WebDriverWait(search_page, 10).until(
            EC.presence_of_element_located((By.ID, "CaseSearchValue"))
        )
    except:
        logger.error(f"Could not type query to search for case {case_id}")
        return None
    finally:
        search_box.send_keys(case_id)
        search_button = search_page.find_element_by_name("SearchSubmit")
        search_button.click()
        search_page.implicitly_wait(1)
        search_page_content = search_page.page_source

    try:
        register_link = WebDriverWait(search_page, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, case_id))
        )
        register_link.click()
    except:
        logger.error(f"Could not click search result for case {case_id}")
        return None

    try:
        register_heading = WebDriverWait(search_page, 10).until(
            EC.presence_of_element_located((By.ID, "PIr11"))
        )
    except:
        logger.error(f"Could not load register of actions for case {case_id}")
        return None
    finally:
        register_page_content = search_page.page_source
        return search_page_content, register_page_content

def load_court_calendar():
    #open the court calendar, to scrape Settings
    start_page = load_start_page()
    try:
        element = WebDriverWait(start_page, 10).until(
            EC.presence_of_element_located(
                (By.LINK_TEXT, "Court Calendar")
            )
        )
    finally:
        element.click()
        return start_page
    return None

def query_settings(afterdate: str, beforedate: str):
    for tries in range(5):
        #select Date Range radiobutton for search
        try:
            court_calendar = load_court_calendar()
            date_range_radio_button = WebDriverWait(court_calendar, 10).until(
                EC.presence_of_element_located((By.ID, "DateRange"))
            )
            date_range_radio_button.click()
            break
        except:
            logger.error(f"Could not click button to search settings by Date Range, try {tries}")

    #deselect all Case Category checkboxes besides Civil
    for check_id in ["chkDtRangeProbate", "chkDtRangeFamily", "chkDtRangeCriminal"]:
        try:
            category_checkbox = WebDriverWait(court_calendar, 10).until(
                    EC.presence_of_element_located((By.ID, check_id))
                )
            if category_checkbox.is_selected():
                category_checkbox.click()
        except:
            logger.error(f"Could not uncheck {check_id}")
            
    #enter before date
    try:
        after_box = WebDriverWait(court_calendar, 10).until(
            EC.presence_of_element_located((By.ID, "DateSettingOnAfter"))
        )
        after_box.clear()
        after_box.send_keys(afterdate)
    except:
        logger.error(f"Could not type in after date {afterdate}")
        
    #enter after date
    try:
        before_box = WebDriverWait(court_calendar, 10).until(
            EC.presence_of_element_located((By.ID, "DateSettingOnBefore"))
        )
        before_box.clear()
        before_box.send_keys(beforedate)
    except:
        logger.error(f"Could not type in before date {beforedate}")    

    #click search button
    try:
        settings_link = WebDriverWait(court_calendar, 10).until(
            EC.presence_of_element_located((By.ID, "SearchSubmit"))
        )
        settings_link.click()
    except:
        logger.error(f"Could not click search result for dates {beforedate} {afterdate}")

    finally:
        calendar_page_content = court_calendar.page_source
        return calendar_page_content
