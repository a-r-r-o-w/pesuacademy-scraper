import argparse

parser = argparse.ArgumentParser(description = 'Command line notes/slides scraper for www.pesuacademy.com')
options = parser.add_mutually_exclusive_group()
parser.add_argument('username', help = 'Login username', type = str)
parser.add_argument('password', help = 'Login password', type = str)
parser.add_argument('-s', '--semester', help = 'Scrape for given semester', type = int, required = True, metavar = 'S')

options.add_argument('-q', '--quiet', action = 'store_true', help = 'No logging')
options.add_argument('-v', '--verbose', action = 'store_true', help = 'Complete logging')

args = parser.parse_args()