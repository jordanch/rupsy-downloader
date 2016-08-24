# TODO: feature - download music based on style & date | quantity
# TODO: construct more logical download tree with meta data
# TODO: open user's file explorer after download

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
