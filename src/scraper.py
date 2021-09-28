import functools
import logging
import os
import requests
import sys
import time

from bs4 import BeautifulSoup
from clint.textui import progress

logging.basicConfig(format = '[%(levelname)s - %(asctime)s]: %(message)s',
                    datefmt ='%Y-%m-%d %H:%M:%S',
                    handlers = [
                        logging.FileHandler('debug.log'),
                        logging.StreamHandler(sys.stdout)
                    ],
                    level = logging.INFO)

class cd:
    def __init__(self, new_dir: str):
        self.old_dir = os.getcwd()
        self.new_dir = new_dir.encode('ascii', 'ignore').decode()

        for character in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
            if character in self.new_dir:
                self.new_dir = self.new_dir.replace(character, '_')

    def __enter__(self):
        try:
            os.makedirs(self.new_dir)
        except FileExistsError:
            logging.info(f'Directory {self.new_dir} already exists!')
        else:
            logging.info(f'Creating directory {self.new_dir}')

        os.chdir(self.new_dir)

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.old_dir)

# def cd (new_dir: str):
#     def method_getter (method):
#         @functools.wraps(method)
#         def param_getter (*args, **kwargs):
#             try:
#                 os.makedirs(new_dir)
#             except FileExistsError:
#                 logging.info(f'Directory {new_dir} already exists!')
#             else:
#                 logging.info(f'Creating directory {new_dir}')
#
#             old_dir = os.getcwd()
#             os.chdir(new_dir)
#             return_value = method(*args, **kwargs)
#             os.chdir(old_dir)
#
#             return return_value
#         return param_getter
#     return method_getter

class PESUAcademyClient:
    """Class that manages all HTTP(s) requests with www.pesuacademy.com"""

    def __init__ (self, username: str, password: str):
        self.username = username
        self.password = password

        self.cookies    = None
        self.csrf_token = None
        self.subjects   = None

    def login (self):
        logging.info('Logging in')
        logging.debug(f'Username: {self.username}, Password: {self.password}')

        # Send a request to the main page to get cookies and csrf-token
        url = 'https://www.pesuacademy.com/Academy/'
        r = requests.get(url)
        soup = BeautifulSoup(r.text, features = 'lxml')

        logging.debug(f'Request to {url} completed with status: {r.status_code}')

        # Setup cookies and data for next request
        self.cookies = r.cookies
        self.csrf_token = soup.find('meta', {'name': 'csrf-token'})['content'].encode('ascii', 'ignore').decode()
        data = {
            'j_username': self.username,
            'j_password': self.password,
            '_csrf': self.csrf_token
        }

        logging.debug(f'Request to {url} has cookies: {self.cookies}')

        # Login to users account
        url = 'https://www.pesuacademy.com/Academy/j_spring_security_check'
        r = requests.post(url, cookies = self.cookies, data = data)
        soup = BeautifulSoup(r.text, features = 'lxml')

        logging.debug(f'Request to {url} completed with status: {r.status_code}')

        name = soup.find('h4', {'class': 'info_header'}).text.strip().encode('ascii', 'ignore').decode()
        srn = soup.find('span', {'class': 'info_text'}).text.strip().encode('ascii', 'ignore').decode()
        srn = ' '.join(srn.split()[2:]).encode('ascii', 'ignore').decode()

        logging.info(f'Logged in as {name} ({srn})!')

        # The cookies change before and after the login request
        # We need the new cookies to be able to perform other scraping operations
        new_cookies = r.request.headers['Cookie'].split(';')
        for cookie in new_cookies:
            c = cookie.strip().split('=')
            self.cookies.set(c[0], None)
            self.cookies.set(c[0], c[1])

        logging.debug(f'Cookies updated! Set to: {self.cookies}')

        url = 'https://www.pesuacademy.com/Academy/s/studentProfilePESU'
        r = requests.get(url, cookies = self.cookies)
        soup = BeautifulSoup(r.text, features = 'lxml')

        logging.debug(f'Request to {url} completed with status: {r.status_code}')

        self.csrf_token = soup.find('meta', {'name': 'csrf-token'})['content'].encode('ascii', 'ignore').decode()

    def logout (self):
        pass

    def my_courses (self, semester: int):
        logging.info('Selecting "My Courses"')

        # After login, I think that the dashboard page loads the html for the
        # sidebar dynamically and therefore is invisible on the page html data
        # As I can't retrieve the menu id's automatically, I need to resort to
        # using raw values
        data = {
            'controllerMode': '6403',
            'actionType': '38',
            'id': '1153',
            'menuId': '653',
            '_csrf': self.csrf_token
        }

        url = 'https://www.pesuacademy.com/Academy/s/studentProfilePESUAdmin'
        r = requests.post(url, cookies = self.cookies, data = data)
        soup = BeautifulSoup(r.text, features = 'lxml')

        logging.warning('Using raw values collected manually as query parameters. Try automating the process!')
        logging.debug(f'Request to {url} completed with status: {r.status_code}')
        logging.info('Collecting semester data')

        url = 'https://www.pesuacademy.com/Academy/a/studentProfilePESU/getStudentSemestersPESU'
        r = requests.get(url, cookies = self.cookies)
        soup = BeautifulSoup(r.text, features = 'lxml')

        logging.debug(f'Request to {url} completed with status: {r.status_code}')

        semester_ids = {option.text.strip()[-1]: option['value'].replace('\\', '')[1:-1]
                        for option in soup.find_all('option')}

        logging.debug(f'Found semesters: {semester_ids}')

        semester = str(semester)
        if semester not in semester_ids.keys():
            logging.error('Semester not found! Cannot proceed with scraping...')
            exit()

        semester_id = semester_ids[semester]

        logging.info(f'Selecting "My Courses" for semester {semester} (id: {semester_id})')

        data = {
            'controllerMode': '6403',
            'actionType': '38',
            'id': semester_id,
            'menuId': '653',
            '_csrf': self.csrf_token
        }

        url = 'https://www.pesuacademy.com/Academy/s/studentProfilePESUAdmin'
        r = requests.post(url, cookies = self.cookies, data = data)
        soup = BeautifulSoup(r.text, features = 'lxml')

        logging.warning('Using raw values collected manually as query parameters. Try automating the process!')
        logging.debug(f'Request to {url} completed with status: {r.status_code}')

        self.subjects = [[
            *[data.text.strip().encode('ascii', 'ignore').decode() for data in row.find_all('td')],
            row['id'][row['id'].find('_') + 1 :].encode('ascii', 'ignore').decode()
        ] for row in soup.find('tbody').find_all('tr')]

        for s in self.subjects:
            print(self._subject_formatter(s))
        pretty_subjects = '\n'.join('{index:<5} {name:<50} {id:<15} - {course_type:<15} - Status: {status:<10}'
                                    .format(index = f'({index})',
                                            **self._subject_formatter(subject))
                                    for index, subject in enumerate(self.subjects, start = 1))

        logging.info(f'Found subjects:\n{pretty_subjects}')

    def scrape_subjects (self):
        for i in range(6, len(self.subjects)):
            self.scrape_subject(index = i)

    def scrape_subject (self, index: int):
        subject = self.subjects[index]

        logging.info('Scraping subject: {name} {id} - {course_type} - Status: {status}'
                     .format(**self._subject_formatter(subject)))

        data = {
            'controllerMode': '6403',
            'actionType': '42',
            'id': subject[-1],
            'menuId': '653',
            '_csrf': self.csrf_token
        }

        url = 'https://www.pesuacademy.com/Academy/s/studentProfilePESUAdmin'
        r = requests.get(url, cookies = self.cookies, data = data)
        soup = BeautifulSoup(r.text, features = 'lxml')

        logging.warning('Using raw values collected manually as query parameters. Try automating the process!')
        logging.debug(f'Request to {url} completed with status: {r.status_code}')

        tab_content = soup.find('div', {'class': 'tab-content'})

        if tab_content is None:
            return

        units = [[unit.text.strip().encode('ascii', 'ignore').decode(),
                  unit['href'][unit['href'].find('_') + 1:]
                  ] for unit in tab_content.find('div', {'id': 'courseUnits'}).find_all('a')]

        pretty_units = '\n'.join(f'({index}) {unit[0]}'
                                 for index, unit in enumerate(units, start = 1))

        logging.info(f'Found the following units:\n{subject[1]}:\n{pretty_units}')

        with cd(f'{subject[1]}'):
            for unit in units:
                self.scrape_unit(unit)

    def scrape_unit (self, unit: [str]):
        logging.info(f'Scraping {unit[0]}')

        data = {
            'controllerMode': '6403',
            'actionType': '43',
            'coursecontentid': unit[1],
            'menuId': '653',
            '_csrf': self.csrf_token
        }

        url = 'https://www.pesuacademy.com/Academy/s/studentProfilePESUAdmin'
        r = requests.get(url, cookies = self.cookies, data = data)
        soup = BeautifulSoup(r.text, features = 'lxml')

        logging.warning('Using raw values collected manually as query parameters. Try automating the process!')
        logging.debug(f'Request to {url} completed with status: {r.status_code}')

        tbody = soup.find('tbody')

        if tbody is not None:
            trs = tbody.find_all('tr')
        else:
            logging.info(f'Found no notes for {unit[0]}!')
            return

        notes = []
        for row in trs:
            try:
                name = row.find('span', {'class': 'short-title'}).text.strip().encode('ascii', 'ignore').decode()
                note = row.find('span', {'class': 'pesu-icon-open-book'}).parent
                offset = note['onclick'].find('(') + 1
                onclick = [i.strip("'")
                           for i in note['onclick'][offset : -1].split(',')]
                onclick = [name, *onclick]
            except:
                pass
            else:
                notes.append(onclick)

        logging.info('Found notes for classes:\n{classes}'
                     .format(classes = '\n'.join(i[0] for i in notes)))

        slides = []
        for row in trs:
            try:
                name  = row.find('span', {'class': 'short-title'}).text.strip().encode('ascii', 'ignore').decode()
                slide = row.find('span', {'class': 'pesu-icon-presentation-graphs'}).parent
                offset = slide['onclick'].find('(') + 1
                onclick = [i.strip("'")
                           for i in slide['onclick'][offset: -1].split(',')]
                onclick = [name, *onclick]
            except:
                pass
            else:
                slides.append(onclick)

        logging.info('Found notes for classes:\n{classes}'
                     .format(classes = '\n'.join(i[0] for i in notes)))

        with cd(unit[0]), cd('Notes'):
            self.scrape_notes(notes)

        with cd(unit[0]), cd('Slides'):
            self.scrape_slides(slides)

    def scrape_notes (self, notes):
        for num, note in enumerate(notes, start = 1):
            note[0] = f'({num}) {note[0]}'

            data = {
                'url': 'studentProfilePESUAdmin',
                'controllerMode': '6403',
                'actionType': '60',
                'selectedData': note[2],
                'id': note[5],
                'unitid': note[1],
                'menuId': '653'
            }

            url = 'https://www.pesuacademy.com/Academy/s/studentProfilePESUAdmin'
            r = requests.get(url, cookies = self.cookies, data = data)
            soup = BeautifulSoup(r.text, features = 'lxml')

            logging.warning('Using raw values collected manually as query parameters. Try automating the process!')
            logging.debug(f'Request to {url} completed with status: {r.status_code}')

            for index, iframe in enumerate(soup.find_all('iframe'), start = 1):
                src = 'https://www.pesuacademy.com' + iframe['src']
                src = src[: src.find('#')]

                try:
                    r = requests.get(src, cookies = self.cookies, stream = True)
                except:
                    continue

                logging.debug(f'Request to {url} completed with status: {r.status_code}')

                size = int(r.headers.get('content-length'))
                file_name = f'{note[0]}_{index}.pdf'
                for character in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
                    if character in file_name:
                        file_name = file_name.replace(character, '_')

                logging.info(f'Download: {file_name} ({round(size / (1 << 20), 2)} MB)')

                with open(file_name, 'wb') as file:
                    for chunk in progress.bar(r.iter_content(
                            chunk_size = 1 << 10),
                            expected_size = size / (1 << 10) + 1
                    ):
                        if chunk:
                            file.write(chunk)

                time.sleep(1)

    def scrape_slides (self, slides):
        for num, slide in enumerate(slides, start = 1):
            slide[0] = f'({num}) {slide[0]}'

            data = {
                'url': 'studentProfilePESUAdmin',
                'controllerMode': '6403',
                'actionType': '60',
                'selectedData': slide[2],
                'id': slide[5],
                'unitid': slide[1],
                'menuId': '653'
            }

            url = 'https://www.pesuacademy.com/Academy/s/studentProfilePESUAdmin'
            r = requests.get(url, cookies = self.cookies, data = data)
            soup = BeautifulSoup(r.text, features = 'lxml')

            logging.warning('Using raw values collected manually as query parameters. Try automating the process!')
            logging.debug(f'Request to {url} completed with status: {r.status_code}')

            for index, iframe in enumerate(soup.find_all('iframe'), start = 1):
                src = 'https://www.pesuacademy.com' + iframe['src']
                src = src[: src.find('#')]

                try:
                    r = requests.get(src, cookies = self.cookies, stream = True)
                except:
                    continue

                logging.debug(f'Request to {url} completed with status: {r.status_code}')

                size = int(r.headers.get('content-length'))
                file_name = f'{slide[0]}_{index}.pdf'
                for character in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
                    if character in file_name:
                        file_name = file_name.replace(character, '_')

                logging.info(f'Download: {file_name} ({round(size / (1 << 20), 2)} MB)')

                with open(file_name, 'wb') as file:
                    for chunk in progress.bar(r.iter_content(
                            chunk_size = 1 << 10),
                            expected_size = size / (1 << 10) + 1
                    ):
                        if chunk:
                            file.write(chunk)

                time.sleep(1)

    @staticmethod
    def _subject_formatter (subject):
        return {
            'name': subject[1],
            'id': f'({subject[0]})',
            'course_type': 'Core Course'     if subject[2] == 'CC' else
                           'Elective Course' if subject[2] == 'EC' else
                           'None',
            'status': subject[3]
        }
