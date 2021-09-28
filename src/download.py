import argparse
import logging

from scraper import (
    PESUAcademyClient,
    cd
)

parser = argparse.ArgumentParser(description = 'Command line notes/slides scraper for www.pesuacademy.com')
options = parser.add_mutually_exclusive_group()
options.add_argument('-q', '--quiet', action = 'store_true', help = 'No logging')
options.add_argument('-v', '--verbose', action = 'store_true', help = 'Complete logging')
parser.add_argument('username', help = 'Login username', type = str)
parser.add_argument('password', help = 'Login password', type = str)
parser.add_argument('-s', '--semester', help = 'Scrape for given semester', type = int, required = True, metavar = 'S')

args = parser.parse_args()

if args.quiet:
    logging.getLogger().setLevel(logging.CRITICAL + 1)
elif args.verbose:
    logging.getLogger().setLevel(logging.DEBUG)

client = PESUAcademyClient(username = args.username,
                           password = args.password)
client.login()
client.my_courses(semester = args.semester)

with cd(f'Sem-{args.semester}'):
    client.scrape_subjects()
client.logout()
