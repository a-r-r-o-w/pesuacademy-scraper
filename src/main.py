import logging

from parser import args
from scraper import (
    PESUAcademyClient,
    cd
)

def main():
    """ set loggin level(if given) """
    if args.quiet:
        logging.getLogger().setLevel(logging.CRITICAL + 1)
    elif args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    """ Invoke the utility """
    client = PESUAcademyClient(username=args.username,
                               password=args.password)
    client.login()
    client.my_courses(semester=args.semester)

    with cd(f'Sem-{args.semester}'):
        client.scrape_subjects()
    client.logout()


main()