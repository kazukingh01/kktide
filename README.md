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
sudo docker exec --user=postgres postgres pg_dump -U postgres -d XXXXX -s \
    -t tide_genbo \
    -t tide_mst_genbo \
    -t tide_suisan \
    -t tide_mst_suisan \
    > ~/schema.sql
```