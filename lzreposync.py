# IMPORTING MODULES
import json
import os
import zipfile
import tarfile
import gzip
import shutil
import requests
from sqlalchemy import create_engine, insert, text
import time
import hashlib
from psycopg2.errorcodes import UNIQUE_VIOLATION
from psycopg2 import errors

time.sleep(5)  # waiting for required packages to load and get initialized

# ARCHIVE EXTENSIONS
ZIP_EXTENSION = ".zip"
TAR_EXTENSION = ".tar"
TAR_GZ_EXTENSION = ".tar.gz"
TGZ_EXTENSION = ".tgz"
GZ_EXTENSION = ".gz"

EMPTY_URL_ERROR = "ERROR: URL should not be empty."
FILENAME_ERROR = "ERROR: Filename should not be empty."
UNKNOWN_FORMAT = "ERROR: Unknown file format. Can't extract."

# db info
postgres_user = "postgres"
postgres_pass = "postgres"
container_ip = "127.0.0.1"

data_dir = "metadata"
metadata_file_location = "metadata/Packages"
packages_metadata_url = "http://archive.ubuntu.com/ubuntu/dists/focal/main/binary-amd64/Packages.gz"


def get_filename(url):
    """Extract filename from file url"""
    filename = os.path.basename(url)
    return filename


def get_file_location(target_path, filename):
    """ Concatenate download directory and filename"""
    return target_path + filename


def extract_file(target_path, filename):
    """Extract file based on file extension target_path: string, location where data will be extracted filename:
    string, name of the file along with extension"""
    if filename == "" or filename is None:
        raise Exception(FILENAME_ERROR)

    file_location = get_file_location(target_path, filename)

    if filename.endswith(ZIP_EXTENSION):
        print("Extracting zip file...")
        zipf = zipfile.ZipFile(file_location, 'r')
        zipf.extractall(target_path)
        zipf.close()
    elif filename.endswith(TAR_EXTENSION) or \
            filename.endswith(TAR_GZ_EXTENSION) or \
            filename.endswith(TGZ_EXTENSION):
        print("Extracting tar file")
        tarf = tarfile.open(file_location, 'r')
        tarf.extractall(target_path)
        tarf.close()
    elif filename.endswith(GZ_EXTENSION):
        print("Extracting gz file")
        out_file = file_location[:-3]
        with gzip.open(file_location, "rt") as f_in:
            with open(out_file, "w") as f_out:
                shutil.copyfileobj(f_in, f_out)
    else:
        print(UNKNOWN_FORMAT)


def download_dataset(url, target_path="metadata/", keep_download=True, overwrite_download=False):
    if url == "" or url is None:
        raise Exception(EMPTY_URL_ERROR)

    filename = get_filename(url)
    file_location = get_file_location(target_path, filename)

    os.makedirs(data_dir, exist_ok=True)

    if os.path.exists(file_location) and not overwrite_download:
        print(f"File already exists at {file_location}. Use: 'overwrite_download=True' to \
overwrite download")
        extract_file(target_path, filename)
        return

    print(f"Downloading file from {url} to {file_location}.")
    # Download
    with open(file_location, 'wb') as f:
        with requests.get(url, allow_redirects=True, stream=True) as resp:
            if resp.status_code == 200:
                for chunk in resp.iter_content(chunk_size=512):  # chunk_size in bytes
                    if chunk:
                        f.write(chunk)
            else:
                print(f"Error: Status code {resp.status_code} - {resp.reason}")
                return

    print("Finished downloading.")
    print("Extracting the file now ...")
    extract_file(target_path, filename)

    if not keep_download:
        os.remove(file_location)

    return True


def get_db_instance():
    #  Init db and return connection instance
    engine = create_engine("postgresql+psycopg2://%s:%s@%s:5432/DB" % (postgres_user, postgres_pass, container_ip))
    conn = engine.connect()
    return conn


def insert_package_metadata(pkg_metadata_dict: dict, attrs_len: int, conn):
    col_names = list(pkg_metadata_dict.keys())
    values = list(pkg_metadata_dict.values())
    values = list(map(lambda val: "'"+val+"'", values))  # formatting values for sql. Adding ' ' quotes
    insert_query = "INSERT INTO package_meta_data ({}) VALUES ({});".format(", ".join(col_names), ", ".join(values))

    #print("Query: ", insert_query)
    try:
        conn.execute(text(insert_query))
        conn.commit()
    except errors.UniqueViolation as e:
        raise e


def save_package_metadata(package: str, conn) -> bool:
    """Save the given package metadata into the local db"""
    metadata_attributes = package.split("\n")
    pkg_name = metadata_attributes[0].split(": ")[0]
    metadata_dict = {}
    for attr in metadata_attributes:
        attr_name = attr.split(": ")[0]
        attr_val = attr.split(": ")[1]
        if attr_name == "Section" or attr_name == "Size":
            # Section & Size are Postgres keywords
            attr_name += "P"
        elif "-" in attr_name:
            #  hyphen is not allowed
            attr_name = attr_name.replace("-", "_")
        metadata_dict[attr_name] = attr_val

    # calculate object digest to avoid insert duplication
    pkg_digest = hashlib.sha256(json.dumps(metadata_dict, sort_keys=True).encode()).hexdigest()
    metadata_dict["digest"] = pkg_digest
    try:
        insert_package_metadata(metadata_dict, len(metadata_dict), conn)
    except errors.UniqueViolation as e:
        #  TODO: this is not working for some reason
        print("WARNING: %s already inserted in the database!" % pkg_name)
    except:
        # TODO: handle small exceptions
        pass
def parse_metadata_and_save_to_db():
    """Parse the 'Pacakge' file (metadata file), extract metadata and save the data into a local postgres db"""
    conn = get_db_instance()
    with open(metadata_file_location, "r") as md_file:
        md_content = md_file.read()
        packages_list = md_content.split("\n\n")
        for package in packages_list:
            if len(package) > 0:
                package_obj = save_package_metadata(package, conn)  # save to local db
                print("INFO: saving package %s" % package.split("\n")[0].split(": ")[1])


if __name__ == "__main__":
    # metadata_downloaded = download_dataset(packages_metadata_url, keep_download=False, overwrite_download=True)
    # if metadata_downloaded:
    #     parse_metadata_and_save_to_db()
    parse_metadata_and_save_to_db()