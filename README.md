# kktide
Collecting and analyze the TIDE's data

This data is collected via below public website.
https://www.data.jma.go.jp/kaiyou/db/tide/suisan/index.php

Observation point list.
https://www.data.jma.go.jp/gmd/kaiyou/db/tide/genbo/station.php


# Install PostgreSQL

```bash
DOCKER_VER="17.4"
echo "FROM postgres:${DOCKER_VER}" > ~/Dockerfile
echo "RUN apt-get update" >> ~/Dockerfile
echo "RUN apt-get install -y locales" >> ~/Dockerfile
echo "RUN rm -rf /var/lib/apt/lists/*" >> ~/Dockerfile
echo "RUN localedef -i ja_JP -c -f UTF-8 -A /usr/share/locale/locale.alias ja_JP.UTF-8" >> ~/Dockerfile
echo "ENV LANG ja_JP.utf8" >> ~/Dockerfile
cd ~
sudo docker image build -t postgres:${DOCKER_VER}.jp .
sudo mkdir -p /var/local/postgresql/data
sudo docker run --name postgres \
    -e POSTGRES_PASSWORD=postgres \
    -e POSTGRES_INITDB_ARGS="--encoding=UTF8 --locale=ja_JP.utf8" \
    -e TZ=Asia/Tokyo \
    -v /var/local/postgresql/data:/var/lib/postgresql/data \
    -v /home/share:/home/share \
    -d postgres:${DOCKER_VER}.jp
sudo docker exec --user=postgres postgres dropdb tide
sudo docker exec --user=postgres postgres createdb --encoding=UTF8 --locale=ja_JP.utf8 --template=template0 tide
```

# Import schema

```bash
cd ~
git clone https://github.com/kazukingh01/kktide.git
cp ~/kktide/main/schema.sql /home/share/
sudo docker exec --user=postgres postgres psql -U postgres -d XXXXX -f /home/share/schema.sql 
```

# Dump schema

```bash
sudo docker exec --user=postgres postgres pg_dump -U postgres -d XXXXX -s \
    -t tide_genbo \
    -t tide_mst_genbo \
    -t tide_suisan \
    -t tide_mst_suisan \
    > ~/schema.sql
```

# How to use

### Update MST

```bash
python get_genbo_mst.py  --update --host 172.17.0.2 --port 5432 --user postgres --pwd postgres --db tide 
python get_suisan_mst.py --update --host 172.17.0.2 --port 5432 --user postgres --pwd postgres --db tide 
```

### Data

```bash
python get_genbo.py  --date 202403 --since 202401 --update --host 172.17.0.2 --port 5432 --user postgres --pwd postgres --db tide 
python get_suisan.py --year 2024                  --update --host 172.17.0.2 --port 5432 --user postgres --pwd postgres --db tide 
```

### Plot

```bash
python plot.py --list
python -i plot.py --fr 20240301 --to 20240305 --suisan --s ZL --showtime
python show_map.py --csv XXXXX.csv
```