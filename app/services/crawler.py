import requests
import scrapy
from scraperapi_sdk import ScraperAPIClient
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
import pandas as pd
import time

from app.schemas.crawler import PlaneInfo, SearchForm
from app.utils.logger import get_logger

logger = get_logger()


def save_to_csv(plane_infos: list[PlaneInfo]):
    df = pd.DataFrame(plane_infos)
    df.to_csv('plane_infos.csv', index=False, encoding='utf-8-sig')


class CrawlerService:
    """爬虫服务"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CrawlerService, cls).__new__(cls)
            cls._instance.__init__()
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            options = webdriver.ChromeOptions()
            options.add_argument(f"user-agent={UserAgent().random}")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            self.wait = WebDriverWait(self.driver, 20)
            self.initialized = True
            logger.info("初始化webdriver成功")

        try:
            self.codes = pd.read_csv("../static/airportcodes.csv", encoding='gbk')
            logger.info("初始化三字码转换器成功")
        except Exception as e:
            logger.error(f"初始化三字码转换器失败:{e}")
            self.codes = None

    def get_airport_code(self, city_name: str) -> str | None:
        try:
            result = self.codes.query(f"城市名称 == '{city_name}'")

            if not result.empty:
                return result.iloc[0]['机场三字码']
            else:
                return None
        except Exception as e:
            logger.error(f"发生错误{e}")
            return None

    def construct_url(self, search_form: SearchForm) -> str:
        base_url = "https://www.ly.com/flights/itinerary/oneway/{dep_city_code}-{arr_city_code}?from={departure_city}&to={arrival_city}&date={departure_date}"
        departure_city = search_form.departure_city
        arrival_city = search_form.arrival_city

        url = base_url.format(
            dep_city_code=self.get_airport_code(departure_city),
            arr_city_code=self.get_airport_code(arrival_city),
            departure_date=search_form.departure_date,
            departure_city=departure_city,
            arrival_city=arrival_city
        )
        return url

    def crawl_plane_infos_plus(self, search_form: SearchForm):
        url = self.construct_url(search_form)
        client = ScraperAPIClient('e341e296caba2a24969385b8b0ed35a2')
        result = client.get(url=url, params={'render': True})
        self.parse(result)
        print(result)


    def parse(self, response):
        flights = response.css('.flight-item-head')
        for flight in flights:
            plane_info = {
                'airline': flight.css('.head-item-info .flight-name-new .flight-item-name::text').get(),
                'aircraft_type': flight.css('.head-item-info .flight-name-new .flight-item-type::text').get(),
                'departure_time': flight.css('.head-times-info .f-startTime.f-times-con::text').get(),
                'flight_duration': flight.css('.head-times-info .f-line-to::text').get(),
                'arrival_time': flight.css('.head-times-info .f-endTime.f-times-con::text').get(),
                'price': flight.css('.head-prices::text').get() or "未显示"
            }

            print(plane_info)
            yield plane_info

    def crawl_plane_infos_test(self, search_form: SearchForm):
        return

    def crawl_plane_infos(self, search_form: SearchForm):
        try:
            url = self.construct_url(search_form)
            self.driver.get(url)

            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'flight-item-head')))
            time.sleep(5)

            self.scroll_to_bottom()

            plane_infos = []
            flights = self.driver.find_elements(By.CLASS_NAME, 'flight-item-head')

            for flight in flights:
                plane_info = PlaneInfo()
                try:
                    plane_info.airline = flight.find_element(By.CSS_SELECTOR,
                                                             '.head-item-info .flight-name-new .flight-item-name').text
                    plane_info.aircraft_type = flight.find_element(By.CSS_SELECTOR,
                                                                   '.head-item-info .flight-name-new .flight-item-type').text
                    plane_info.departure_time = flight.find_element(By.CSS_SELECTOR,
                                                                    '.head-times-info .f-startTime.f-times-con').text
                    plane_info.flight_duration = flight.find_element(By.CSS_SELECTOR,
                                                                     '.head-times-info .f-line-to').text
                    plane_info.arrival_time = flight.find_element(By.CSS_SELECTOR,
                                                                  '.head-times-info .f-endTime.f-times-con').text

                    try:
                        plane_info.price = flight.find_element(By.CSS_SELECTOR, '.head-prices').text
                    except:
                        plane_info.price = "未显示"

                    plane_infos.append(plane_info)

                except Exception as e:
                    logger.error(f"提取单个航班信息时出错: {e}")
                    continue

            if plane_infos:
                save_to_csv(plane_infos)
            else:
                logger.info("未找到航班信息")

        except Exception as e:
            logger.error(f"发生错误: {e}")

        finally:
            self.driver.quit()

    def scroll_to_bottom(self):
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height


crawler_service = CrawlerService()

if __name__ == "__main__":
    search_form = SearchForm(
        departure_date="2025-02-25",
        departure_city="北京",
        arrival_city="杭州"
    )

    crawler_service.crawl_plane_infos(search_form)
