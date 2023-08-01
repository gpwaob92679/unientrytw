import datetime
import json
import os
from pathlib import Path
from typing import Any

import bs4
import django
import requests_cache

import third_party.cf_clearance_scraper.main as cf_clearance_scraper

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unientrytw.settings')
django.setup()
import db.models


class UniversityScraper:

    def __init__(self):
        self.session = requests_cache.CachedSession(
            expire_after=datetime.timedelta(days=1))

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

    def get_schools(self, year: int | str):
        response = self.session.get(
            f'https://www.com.tw/cross/university_list{year}.html')
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'id': 'table1'})

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
            school.save()


def main():
    scraper = UniversityScraper()
    scraper.get_schools(112)


if __name__ == '__main__':
    main()
