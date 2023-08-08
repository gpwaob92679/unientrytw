import datetime
import json
import logging
import os
from pathlib import Path
import re
import sys
import time

import bs4
import django
import requests_cache
import xlrd

import third_party.cf_clearance_scraper.main as cf_clearance_scraper

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unientrytw.settings')
django.setup()
import db.models

logger = logging.getLogger(__name__)
logger.setLevel('INFO')
logger.addHandler(logging.StreamHandler(sys.stderr))


def response_hook(response, *args, **kwargs) -> None:
    if not isinstance(response, requests_cache.AnyResponse):
        return
    logger.info('Request URL: %s', response.url)
    if response.from_cache:
        logger.info('Reading from local cache')
    else:
        logger.info('Sending request to remote')
        time.sleep(2)  # Throttling.


class WwwComTwScraper:

    def __init__(self):
        self.session = requests_cache.CachedSession(
            expire_after=datetime.timedelta(days=1))
        self.session.hooks['response'].append(response_hook)

        self.clearance_file = Path('clearance.json')
        self.get_clearance()

    def get_clearance(self) -> None:

        def challenge_detected(text: str) -> bool:
            for platform in ('non-interactive', 'managed', 'interactive'):
                if f"cType: '{platform}'" in text:
                    return True
            return False

        def load_and_set_clearance():
            with open(self.clearance_file, 'r', encoding='utf-8') as f:
                clearance = json.load(f)['clearance_cookies'][-1]
                self.session.headers['User-Agent'] = clearance['user_agent']
                self.session.cookies.set('cf_clearance',
                                         clearance['cf_clearance'],
                                         domain=clearance['domain'])

        def get_new_clearance():
            cf_clearance_scraper.main(
                ['-f', str(self.clearance_file), 'https://www.com.tw/'])
            load_and_set_clearance()

        if self.clearance_file.exists():
            load_and_set_clearance()
            response = self.session.get('https://www.com.tw/')
            if challenge_detected(response.text):
                get_new_clearance()
        else:
            get_new_clearance()

    def __del__(self):
        self.session.close()

    def _get_main_table(self, url: str) -> bs4.Tag:
        response = self.session.get(url)
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        return soup.find('div', {
            'class': 'homepagetitle'
        }).find_next_sibling('table')

    def get_schools(self, year: int | str):
        table = self._get_main_table(
            f'https://www.com.tw/cross/university_list{year}.html')
        for td in table.find_all('td', {
                'align': 'center',
                'id': 'university_list_row_height'
        }):
            a = td.find('a')
            school = db.models.School(
                id=a.next_element.strip(' \n'),
                name=a.next_sibling.next_element.strip(' \n'))
            if not school.id:
                school.id = td.find('span', {
                    'class': 'schoolid'
                }).next_element.strip(' \n')
            logger.info(school)
            school.save()

    def get_departments(self, year: int | str) -> None:
        for school in db.models.School.objects.all():
            table = self._get_main_table(
                f'https://www.com.tw/cross/university_{school.id}_{year}.html')
            for tr_department in table.find_all(
                    lambda tr: tr.name == 'tr' and len(tr.find_all('td')) == 5):
                tds = tr_department.find_all('td')
                department = db.models.Department(id=tds[0].text[1:-1],
                                                  name=tds[1].text,
                                                  school=school)
                logger.info(department)
                department.save()


class CeecWorkbookScraper:

    def __init__(self):
        self.session = requests_cache.CachedSession('ceec_http_cache')

    def get_divisions_and_rooms(self) -> None:
        response = self.session.get('https://www.ceec.edu.tw/files/file_pool/1/0N117365953363303233/%E5%90%84%E8%80%83%E5%8D%80%E5%8F%8A%E5%90%84%E5%88%86%E5%8D%80%E8%A9%A6%E5%A0%B4%E8%80%83%E7%94%9F%E4%BA%BA%E6%95%B8%E7%B5%B1%E8%A8%88%E8%A1%A8.xls')  # yapf: disable
        workbook = xlrd.open_workbook(file_contents=response.content)
        sheet = workbook.sheet_by_index(0)
        for row in sheet.get_rows():
            if row[1].ctype == xlrd.XL_CELL_NUMBER:
                division_id = int(row[1].value)
                division_name = re.sub(r'^\([^()]*\)', '', row[2].value)
                try:
                    division = db.models.ExamDivision.objects.get(
                        id=division_id)
                except db.models.ExamDivision.DoesNotExist:
                    division = db.models.ExamDivision(id=division_id,
                                                      name=division_name)
                    division.save()
                logger.info(division)

                rooms = range(int(row[3].value), int(row[4].value))
                logger.info('Rooms: [%s, %s]', rooms.start, rooms.stop)
                for room_id in rooms:
                    room = db.models.ExamRoom(id=room_id, division=division)
                    room.save()
                    logger.debug(room)


def main():
    web_scraper = WwwComTwScraper()
    web_scraper.get_schools(112)
    web_scraper.get_departments(112)

    workbook_scraper = CeecWorkbookScraper()
    workbook_scraper.get_divisions_and_rooms()


if __name__ == '__main__':
    main()
