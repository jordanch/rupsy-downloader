# TODO: feature - download music based on style & date | quantity
import os
import re
import datetime

import requests
import shutil
from bs4 import BeautifulSoup


def main():
    print_header()
    releases = get_user_selection_and_links()
    print(releases)
    download_selection(releases)


def print_header():
    print('----------------------------------------')
    print('--------RUPSY DOWNLOAD PROGRAM----------')
    print('----------------------------------------')


def get_user_selection_and_links():

    # flag = False
    # correct_choices = ('f', 'd', 'p', 's', 'a', 'g', 't', 'y', 'e', 'r', 'n', 'o', 'w')
    # while not flag:
    #     choice = input('\nWhich psy genre do you want?\n\n[F]ull-on\n[D]ark Psy\n[P]sy Prog\nP[s]y Chill\n[A]mbient\n'
    #                   '[G]oa Trance\nPsy [T]rance\nPs[y] Breaks\nPsy T[e]chno\nFo[r]rest Psy\n[N]ight Full-on Psy\n'
    #                   'Su[o]mi\nDo[w]n Tempo\n\nEnter your selection: ')
    #
    #     choice = choice.lower().strip(" ")
    #     if choice in correct_choices:
    #         if choice == 'f':
    #             choice = 'Full-On'
    #         elif choice == 'd':
    #             choice = 'Dark Psy'
    #         elif choice == 'p':
    #             choice = 'Psy Prog'
    #         elif choice == 's':
    #             choice = 'Psy Chill'
    #         elif choice == 'a':
    #             choice = 'Ambient'
    #         elif choice == 'g':
    #             choice = 'Goa Trance'
    #         elif choice == 't':
    #             choice = 'Psy Trance'
    #         elif choice == 'y':
    #             choice = 'Psy Breaks'
    #         elif choice == 'e':
    #             choice = 'Psy Techno'
    #         elif choice == 'r':
    #             choice = 'Forrest Psy'
    #         elif choice == 'n':
    #             choice = 'Night Full-On Psy'
    #         elif choice == 'o':
    #             choice = 'Suomi'
    #         elif choice == 'w':
    #             choice = 'Down Tempo'
    #
    #         confirm_selection = input('\nAre you happy with your choice: {}\n[C]ontinue or [r]e-select: '.format(choice))\
    #             .lower().strip()
    #         if confirm_selection == 'c':
    #             flag = True
    #         elif confirm_selection != 'r' and confirm_selection != 'c':
    #             print('\nPlease make a valid selection')
    #             continue
    #     else:
    #         print('\nPlease make a valid selection')
    #         continue
    #
    # date_choice = input('\nDo you want music from within a date range? [Y]es / [N]o.\nIf you decide to not download ' +
    #                    'music from a date range, the starting point will be today and the end date will be ' +
    #                    'determined by the next step wherein you choose the amount of music to download ' +
    #                    '(MB or GB or all music)').lower().strip(" ")
    # if date_choice == 'y':
    #     date_start_flag = False
    #     while not date_start_flag:
    #         # TODO: validation on start date based on rupsy min
    #         start_date = input('\nEnter in a start date in this format: YYYY/MM\nRupsy has music from 2005: ').lower().strip(" ")
    #         # TODO: regex for month and date input
    #         if len(start_date) != 7:
    #             print('\nPlease enter a valid date format')
    #             continue
    #         else:
    #             start_date = datetime.date(*list(map(lambda e: int(e), (start_date + '/01').split('/'))))
    #             date_end_flag = False
    #             while not date_end_flag:
    #                 end_date = input('\nEnter in an end date in this format: YYYY/MM: ').lower().strip(" ")
    #                 # TODO: regex for month and date input
    #                 if len(end_date) != 7:
    #                     print('\nPlease enter a valid date format')
    #                     continue
    #                 else:
    #                     end_date = datetime.date(*list(map(lambda e: int(e), (end_date + '/01').split('/'))))
    #                     print('Valid dates')
    #                     date_end_flag = True
    #                     date_start_flag = True
    #     print(start_date.day, end_date)
    # else:
    #     date_range = None
    #
    # data_amount_choice = input('How much music would you like to download?')

    # download music based on artist selection
    # TODO: add validation on input
    artist_selection = input('What artist would you like releases from?\n')
    # scrape site and get URLs for releases for artist
    url = 'http://www.rupsy.ru/index.php'
    host = 'www.rupsy.ru'
    html = requests.get(url + '?id=4&search={0}'.format(artist_selection))
    soup = BeautifulSoup(html.text, 'html.parser')
    releases = soup.find_all('td', class_='rel')
    release_list = []

    for release in releases:

        release_list.append((release.find('div', class_='rel_name').find('a').text,
                             host + release.find('div', style='text-align:center;').find('a')['href']))
    return release_list


def download_selection(releases):

    download_path = os.path.join(os.path.abspath(os.path.curdir), 'rupsy-downloads')
    #   check for folder and create rupsy-download folder if necessary
    if not (os.path.isdir(download_path)):
        os.makedirs(download_path)

    # download releases
    for release in releases:
        # get download filename
        rh = requests.head('http://' + release[1])
        release_download_filename = release[0].replace(' ', '') + '.{0}'\
            .format(rh.headers['Location'].split('.')[-1]).lower()
        # create file if one doesn't exist
        if not (os.path.isfile(os.path.join(download_path, release_download_filename))):

            dir_fd = os.open(download_path, os.O_RDONLY)

            def opener(path, flags):

                return os.open(path, flags, dir_fd=dir_fd)

            r = requests.get('http://' + release[1], stream=True)


            print('Starting release download')


            with open(release_download_filename, 'wb', opener=opener) as fd:
                c = 0

                for chunk in r.iter_content(1024):
                    if c % 1048576 == 0:
                        print('Downloaded 1MB of {0}...'.format(release[0]))
                    fd.write(chunk)
                    c += 1024
            os.close(dir_fd)  # don't leak a file descriptor


            print('Finished downloading {0} to {1}'.format(release[0], download_path))
            # unpacking zip if zip
            if os.path.splitext(os.path.join(download_path, release_download_filename))[1] in ['.zip', '.tar']:
                print('Unpacking compressed file for {0}'.format(release[0]))
                shutil.unpack_archive(os.path.join(download_path, release_download_filename), extract_dir=download_path)
                print('Successfully unpacked file. Deleting compressed source...')
                os.remove(os.path.join(download_path, release_download_filename))
                print('Done!')



        else:
            print('You already have downloaded {0}'.format(release[0]))

if __name__ == '__main__':
    main()
