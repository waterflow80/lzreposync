"""
This is a minimal implementation of the lazy reposync parser.
It downloads the target repository's metadata file(s) from the
given url and parses it(them)
"""

# TODO Check for the signature
# TODO Use SAX parser
# TODO Define the best chunk size (consider calculating the current os's free memory and the file size and extract a formula)
# TODO Evaluate the two versions of the download/ benchmark them/ write some tests about them
# TODO After finishing, complete for all other files, normalize the sql code

import argparse
import requests
import os
import shutil
from urllib.parse import urljoin

CACHE_DIR = './cache/metadata/'  # TODO change it into /var/cache/...
PRIMARY_XML = '00c99a7e67dac325f1cbeeedddea3e4001a8f803c9bf43d9f50b5f1c756b0887-primary.xml.gz' # TODO can the name of this file change ?

def create_args_parser():
    args_parser = argparse.ArgumentParser(description='Lazy reposync service')
    args_parser.add_argument('--url', '-u', help='The target url of the remote repository of which we\'ll '
                                                 'parse the metadata')
    return args_parser


def download_primary_xml_v1(url: str, primary_xml: str):
    """Download the primary-xml file from the given repository url"""
    try:
        primary_xml_url = urljoin(url, primary_xml)
        with requests.get(primary_xml_url, stream=True) as response:
            response.raise_for_status()  # check for status code
            with open(os.path.join(CACHE_DIR, primary_xml), 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                print(f"file {primary_xml} was downloaded successfully!")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {primary_xml} file:", e)


def download_primary_xml_v2(url: str, primary_xml: str):
    """Download the primary-xml file from the given repository url"""
    try:
        primary_xml_url = urljoin(url, primary_xml)
        response = requests.get(primary_xml_url, stream=True)
        with open(os.path.join(CACHE_DIR, primary_xml), 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        print(f"file {primary_xml} was downloaded successfully!")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {primary_xml} file:", e)




def parse_primary_xml():
    pass


def download_and_parse_metadata(program_args):
    if not program_args.url:
        print('Error: target url not defined!')
        raise ValueError('Target url was not provided.')

    repo_url = program_args.url
    # print(repo_url, end='')
    download_primary_xml_v1(repo_url, PRIMARY_XML)
    parse_primary_xml()


if __name__ == '__main__':
    parser = create_args_parser()
    args = parser.parse_args()
    download_and_parse_metadata(args)
