# kktide
Collecting and analyze the TIDE's data

This data is collected via below public website.
https://www.data.jma.go.jp/kaiyou/db/tide/suisan/index.php

Observation point list.
https://www.data.jma.go.jp/gmd/kaiyou/db/tide/genbo/station.php


# Import schema

```bash
cd ~
git clone https://github.com/kazukingh01/kktide.git
cp ~/kktide/main/schema.sql /home/share/
sudo docker exec --user=postgres postgres psql -U postgres -d XXXXX -f /home/share/schema.sql 
```

# Dump schema

```bash
docker image build -t postgres:16.1.jp .

sudo docker exec --user=postgres postgres pg_dump -U postgres -d XXXXX -s \
    -t tide_genbo \
    -t tide_mst_genbo \
    -t tide_suisan \
    -t tide_mst_suisan \
    > ~/schema.sql
```

# How to use

### Set postgres config

```
vi ../kktide/config/psgre.py
```

### Update MST

```bash
python get_genbo_mst.py  --update
python get_suisan_mst.py --update
```

### Data

```bash
python get_genbo.py  --date 202403 --since 202401 --update
python get_suisan.py --year 2024 --update
```

### Plot

```bash
python plot.py --list
python -i plot.py --fr 20240301 --to 20240305 --suisan --s ZL --showtime
python show_map.py --csv XXXXX.csv
```