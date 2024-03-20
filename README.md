# Lazy reposync
A basic, lazy version, implementation of the Uyuni's reposync component using the `Packages` metadata file to extract metadata 

## Main Idea
The main idea of the lazy reposync service is to fetch packages' metadata using the `Packages` file for deb packages or `Primary.xml` file for rpm packages, without downlodaing the packages and extracting the corresponding metadata from these packages.

## How does it work ?
The following flowchart diagram might give an idea on the general lazy reposync service:
![reposync-workflow3 drawio](https://github.com/waterflow80/lzreposync/assets/82417779/c4c640d5-2664-4404-9140-f9f75b02ed20)

## Persistence
The fetched metadata will be stored in a local containerized **Postgres** database in a table called **package_meta_data**. Here's a portion of the content of that table after fetching some packges' metadata using the lzrzposync:
| package | architecture | version | priority | section | origin | ... |
|--|--|--|--|--|--|--|
| accountsservice    | amd64        | 0.6.55-0ubuntu11  | standard  | gnome   | Ubuntu | ... |
| acct               | amd64        | 6.6.4-2           | optional  | admin   | Ubuntu | ... |
| acl                | amd64        | 2.2.53-6          | optional  | utils   | Ubuntu | ... |
| acpi-support       | amd64        | 0.143             | optional  | admin   | Ubuntu | ... |
| acpid              | amd64        | 1:2.0.32-1ubuntu1 | optional  | admin   | Ubuntu | ... |
| adduser            | all          | 3.118ubuntu2      | important | admin   | Ubuntu | ... |
| advancecomp        | amd64        | 2.1-2.1build1     | optional  | utils   | Ubuntu | ... |
| adwaita-icon-theme | all          | 3.36.0-1ubuntu1   | optional  | gnome   | Ubuntu | ... |
| aide               | amd64        | 0.16.1-1build2    | optional  | admin   | Ubuntu | ... |
| aide-common        | all          | 0.16.1-1build2    | optional  | admin   | Ubuntu | ... |

## Run
To setup and run the `lzreposync` service locally, please follow these steps:
```shell
$ git clone https://github.com/waterflow80/lzreposync.git
$ cd lzreposync
$ docker-compose up (preferably in another terminal)
$ pip install -r requirements.txt # note some libraries in this file are not necessary and should have been removed.
$ python3.8 lzreposync # if you notice an error like `psycopg2.errors.SyntaxError: ... don't worry, it's just sql complaining, we haven't completed formatting yet

# Now we can see the metadata saved into our database
$ docker exec -it db bash
$ psql -U postgres -d DB
$ SELECT * FROM package_meta_data; # You should see the metadata saved in the datatabase
```

## Current Limitations
The service will fetch packages metadata from one remote location which is: http://archive.ubuntu.com/ubuntu/dists/focal/main/binary-amd64/Packages.gz.
The current implementation is done for demonstration purposes and not a final implementation. 
