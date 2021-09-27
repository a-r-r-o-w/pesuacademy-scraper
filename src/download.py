import json
import sys
import logging

from scraper import PESUAcademyClient

# help_message = """
# Command line notes/slides scraper for www.pesuacademy.com
#
# Usage: download.py [Options] [<Credentials> <Semester>]
#
# Options:
#   -h, --help   <None>       Show help
#   -a, --all    <None>       Scrape all subjects for given semester
#   -n, --index  <int>        Scrape subject with given index for given semester
#   -l, --list   <None>       Show subject list for given semester
#   -i, --ignore <List[int]>  Ignore subjects with given indices while scraping [NOT IMPLEMENTED YET]
#   -d, --debug  <None>       Enable DEBUG logging (set to INFO by default)
#
# Credentials:
#   -c, --credentials <username:str password:str>  Username and Password for login
#   -f, --file        <filename:str>.json          Json file format:
#                                                    {
#                                                      "username": <USERNAME>,
#                                                      "password": <PASSWORD>
#                                                    }
#
# Semester:
#   -s, --semester <int>  Semester for which notes/slides will be scraped
# """
#
# scrape_all       = False
# display_subjects = False
# username = ''
# password = ''
# semester = None
# index    = None
#
# argc = len(sys.argv)
# argv = sys.argv
#
# if argc == 1 or '-h' in argv or '--help' in argv:
#     print(help_message)
#     exit()
#
# for i in range(1, argc):
#     try:
#         if argv[i] == '-a' or argv[i] == '--all':
#             scrape_all = True
#         elif argv[i] == '-n' or argv[i] == '--index':
#             index = int(argv[i + 1])
#         elif argv[i] == 'l' or argv[i] == '--list':
#             display_subjects = True
#         elif argv[i] == '-d' or argv[i] == '--debug':
#             logging.getLogger().setLevel(logging.DEBUG)
#         elif argv[i] == '-f' or argv[i] == '--file':
#             file = argv[i + 1]
#             with open(file, 'r', encoding = 'utf-8') as f:
#                 content = json.loads(f.read())
#             username = content['username']
#             password = content['password']
#         elif argv[i] == '-c' or argv[i] == '--credentials':
#             username = argv[i + 1]
#             password = argv[i + 2]
#         elif argv[i] == '-s' or argv[i] == '--semester':
#             semester = int(argv[i + 1])
#     except Exception:
#         print(help_message)
#         exit()
#
# client = PESUAcademyClient(username = username,
#                            password = password)
# client.login()
# client.my_courses(semester = semester)
#
# if display_subjects:
#     exit()
#
# if scrape_all:
#     for i in range(len(client.subjects)):
#         try:
#             client.scrape_subject(index = i)
#         except:
#             pass
# else:
#     client.scrape_subject(index = index)
#
# client.logout()

with open('env.json', 'r', encoding = 'utf-8') as file:
    content = json.loads(file.read())
semester = 3

client = PESUAcademyClient(username = content['username'],
                           password = content['password'])
client.login()
client.my_courses(semester = semester)
client.scrape_subject(index = 8)
client.logout()
