# -*- coding: utf-8 -*-
from selenium import webdriver
from lxml import etree
import re
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import xlwt


class Lagouspider(object):
    driver_path = r"F:\chorm\chromedriver.exe"
    def __init__(self):
        self.driver = webdriver.Chrome(executable_path=Lagouspider.driver_path)
        self.url = 'https://www.lagou.com/jobs/list_%E5%A4%A7%E6%95%B0%E6%8D%AE%E5%BC%80%E5%8F%91?city=%E6%88%90%E9%83%BD&cl=false&fromSearch=true&labelWords=&suginput='
        self.works = []
    def run(self):
        self.driver.get(self.url)
        while True:
            source = self.driver.page_source
            WebDriverWait(driver = self.driver,timeout = 10).until(EC.presence_of_element_located((By.XPATH,"//div[@class='pager_container']/span[last()]")))
            self.parse_list_page(source)
            try:
                next_btn = self.driver.find_element_by_xpath("//div[@class='pager_container']/span[last()]")
                if "pager_next_disabled" in next_btn.get_attribute("class"):
                    break
                else:
                    next_btn.click()
            except:
                  print("error")
            time.sleep(2)
    def parse_list_page(self,source):
        html = etree.HTML(source)
        links =  html.xpath("//a[@class='position_link']/@href")
        for link in  links:
            self.request_detail_page(link)
            time.sleep(2)
    def request_detail_page(self,url):
        #self.driver.get(url)
        self.driver.execute_script("window.open('%s')"%url)
        self.driver.switch_to.window(self.driver.window_handles[1])
        WebDriverWait(self.driver, timeout=10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='job-name']/span[@class='name']")))
        source = self.driver.page_source
        self.parse_detail_page(source)
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

    def parse_detail_page(self,source):
        html = etree.HTML(source)

        try:
            name = "".join(html.xpath("//span[@class='name']/text()")[0])
            job_request_spans = html.xpath("//dd[@class='job_request']/p//span")
            salary = job_request_spans[0].xpath('.//text()')[0].strip()
            city = job_request_spans[1].xpath('.//text()')[0].strip()
            city = re.sub(r"\s/|/","",city)
            work_years = job_request_spans[2].xpath('.//text()')[0].strip()
            work_years = re.sub(r"\s/","",work_years)
            study = job_request_spans[3].xpath('.//text()')[0].strip()
            study = re.sub(r"\s/","",study)
            description = "".join(html.xpath("//div[@class='job-detail']//p/text()"))
            description = re.sub(r"\s","",description).strip()
            area = "".join(html.xpath("//div[@class='work_addr']/a[2]//text()"))
            address = "".join(html.xpath("//div[@class='work_addr']//text()"))
            address = re.sub("\s|查看地图","",address)
            company = "".join(html.xpath("//div[@class='company']/text()"))
            work = {
                'name': name,
                'city': city,
                'work_years': work_years,
                'study': study,
                'description': description,
                'address': address,
                'area':area,
                'company': company,
                'salary':salary
            }
            self.works.append(work)
            print(work)
            print('='*40)
        except IndexError:
            pass


if __name__ == '__main__':
        spider = Lagouspider()
        spider.run()
        book = xlwt.Workbook(encoding='utf-8')
        sheet = book.add_sheet('work')
        head = ['职位', '城市', '工作年限','学历','工作描述','工作地址','区域','公司','薪资']
        for h in range(len(head)):
            sheet.write(0, h, head[h])  # 写入表头
        i = 1
        for list in work:
            j = 0
            for data in list:
                sheet.write(i, j, data)
                j += 1
            i += 1
book.save('E:\work.xls')