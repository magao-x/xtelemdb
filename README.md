# xtelemdb

Inventory files on one or more hosts in a shared PostgreSQL database and manage replication to a backup medium.

## Usage

TODO

## Installation

```
echo "listen_addresses = '192.168.0.10'" | sudo tee /etc/postgresql/14/main/conf.d/listen_addresses.conf
echo "host    all             all             192.168.0.0/16            scram-sha-256" | sudo tee -a /etc/postgresql/14/main/pg_hba.conf
sudo systemctl restart postgresql
```

```
sudo -u postgres psql
postgres=# CREATE DATABASE xtelem;
CREATE DATABASE
postgres=# CREATE ROLE xsup WITH PASSWORD 'extremeAO!';
```

Grant privileges to the `xsup` user and set up tables:

```
sudo -u postgres psql -d xtelem < setup_users.sql
sudo -u postgres psql -d xtelem < setup.sql
```
