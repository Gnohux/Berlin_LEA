import time
import os
import logging
from platform import system

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

system = system()

logging.basicConfig(
    format='%(asctime)s\t%(levelname)s\t%(message)s',
    level=logging.INFO,
)

class WebDriver:
    def __init__(self):
        self._driver: webdriver.Chrome
        self._implicit_wait_time = 20

    def __enter__(self):
        logging.info("Open browser")
        # some stuff that prevents us from being locked out
        options = webdriver.ChromeOptions() 
        options.add_argument('--disable-blink-features=AutomationControlled')
        self._driver = webdriver.Chrome(options=options)
        self._driver.implicitly_wait(self._implicit_wait_time) # seconds
        self._driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self._driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'})
        return self._driver

    def __exit__(self, exc_type, exc_value, exc_tb):
        logging.info("Close browser")
        self._driver.quit()
        
class BerlinBot:
    def __init__(self):
        self.wait_time = 20
        # self._sound_file = os.path.join(os.getcwd(), "/Users/xuhongwu/PycharmProjects/berlin-auslanderbehorde-termin-bot/alarm.wav")
        self._error_message = "Für die gewählte Dienstleistung sind aktuell keine Termine frei! Bitte"

    @staticmethod
    def enter_start_page(driver):
        logging.info("Visit start page")
        driver.get("https://otv.verwalt-berlin.de/ams/TerminBuchen")
        driver.find_element(By.XPATH, '//*[@id="mainForm"]/div/div/div/div/div/div/div/div/div/div[1]/div[1]/div[2]/a').click()
        time.sleep(5)

    @staticmethod
    def tick_off_some_bullshit(driver):
        logging.info("Ticking off agreement")
        driver.find_element(By.XPATH, '//*[@id="xi-div-1"]/div[4]/label[2]/p').click()
        time.sleep(1)
        driver.find_element(By.ID, 'applicationForm:managedForm:proceed').click()
        time.sleep(5)

    @staticmethod
    def enter_form(driver):
        logging.info("Fill out form")
        # select china
        s = Select(driver.find_element(By.ID, 'xi-sel-400'))
        s.select_by_visible_text("China")
        # eine person
        s = Select(driver.find_element(By.ID, 'xi-sel-422'))
        s.select_by_visible_text("eine Person")
        # with family
        s = Select(driver.find_element(By.ID, 'xi-sel-427' ))
        s.select_by_visible_text("ja")
        time.sleep(1)
        # select china
        s = Select(driver.find_element(By.ID, 'xi-sel-428' ))
        s.select_by_visible_text("China")
        time.sleep(5)
        

        # extend stay
        driver.find_element(By.XPATH, '//*[@id="xi-div-30"]/div[2]/label/p').click()
        time.sleep(2)

        # click on study group
        driver.find_element(By.XPATH, '//*[@id="inner-479-0-2"]/div/div[1]/label/p').click()
        time.sleep(2)

        # b/c of study
        driver.find_element(By.XPATH, '//*[@id="inner-479-0-2"]/div/div[2]/div/div[5]/label').click()
        time.sleep(4)

        # submit form
        driver.find_element(By.ID, 'applicationForm:managedForm:proceed').click()
        time.sleep(10)
    
    def _success(self):
        logging.info("!!!SUCCESS - do not close the window!!!!")
        while True:
            os.system('say "发现Termin"')
            os.system( 'osascript -e \'display notification "通知内容" with title "LEA Termin 已找到" subtitle "副标题"\'' )
            time.sleep(300)
        
        # todo play something and block the browser


    def run_once(self):
        with WebDriver() as driver:
            self.enter_start_page(driver)
            self.tick_off_some_bullshit(driver)
            self.enter_form(driver)

            # retry submit
            for _ in range(10):
                if self._error_message not in driver.page_source:
                    self._success()
                logging.info("Retry submitting form")
                driver.find_element(By.ID, 'applicationForm:managedForm:proceed').click()
                time.sleep(self.wait_time)

    def run_loop(self):
        # play sound to check if it works
        while True:
            logging.info("One more round")
            self.run_once()
            time.sleep(self.wait_time)
            
if __name__ == "__main__":
    BerlinBot().run_loop()