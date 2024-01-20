import bs4, re, datetime, argparse
import requests
import pandas as pd
from kkpsgre.psgre import Psgre
from kktide.config.psgre import HOST, PORT, USER, PASS, DBNAME


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--update", action='store_true', default=False)
    args = parser.parse_args()

    # Get data from HTML
    res = requests.get('https://www.data.jma.go.jp/gmd/kaiyou/db/tide/genbo/station.php')
    res.encoding = 'utf-8'
    soup    = bs4.BeautifulSoup(res.text, 'html.parser')
    table   = soup.find_all("table", attrs={"class": "data2"})[0]
    df      = []
    remarks = None
    for i, spwk in enumerate(table.find_all("tr")):
        if   i == 0: assert len(spwk.find_all("td")) == 0 and len(spwk.find_all("th")) == 10
        elif i == 1: assert len(spwk.find_all("td")) == 0 and len(spwk.find_all("th")) == 2
        elif i == len(table.find_all("tr")) - 1:
            assert len(spwk.find_all("td")) == 1
            remarks = spwk.find_all("td")[0].text.strip()
        else:
            assert len(spwk.find_all("td")) == 11
            se = pd.Series([x.text.strip() for x in spwk.find_all("td")], index=["place_no", "symbol", "name", "location", "latitude", "longitude", "method", "above_dl", "above_tp", "datum_line", "remarks"])
            df.append(se)
    df = pd.concat(df, axis=1, ignore_index=False).T

    # Organize the data
    ## see: https://www.data.jma.go.jp/gmd/kaiyou/db/tide/genbo/explanation.html#station
    df["created_date"]      = datetime.datetime.now().strftime("%Y%m%d")
    df["place_no"]          = df["place_no"].astype(int)
    df["longitude_degrees"] = df["longitude"].str.split("゜").str[0].astype(int)
    df["longitude_minutes"] = df["longitude"].str.split("゜").str[1].str.split("'").str[0].astype(int)
    df["longitude_seconds"] = df["longitude"].str.split("゜").str[1].str.split("'").str[1].str.split('"').str[0].replace("", float("nan")).astype(float)
    df["latitude_degrees" ] = df["latitude" ].str.split("゜").str[0].astype(int)
    df["latitude_minutes" ] = df["latitude" ].str.split("゜").str[1].str.split("'").str[0].astype(int)
    df["latitude_seconds" ] = df["latitude" ].str.split("゜").str[1].str.split("'").str[1].str.split('"').str[0].replace("", float("nan")).astype(float)
    for x in ["above_dl", "above_tp", "datum_line"]:
        df[f"{x}_mm"] = (df[x].replace("^-$", float("nan"), regex=True).astype(float) *  10).fillna(-1).astype(int).replace(-1, float("nan"))
    df["remarks"]           = df["remarks"].map({re.split(r"\s", y)[0].strip():re.split(r"\s", y)[1].strip() for y in [x.strip() for x in remarks.split("\n")]})
    
    # to DB
    if args.update:
        db = Psgre(f"host={HOST} port={PORT} dbname={DBNAME} user={USER} password={PASS}", max_disp_len=200)
        df_check  = db.select_sql("select * from tide_mst_genbo where created_date = (select max(created_date) from tide_mst_genbo);")
        columns   = df_check.columns[1:-1]
        is_insert = True
        if df_check.shape[0] == df.shape[0]:
            ndf_check = df_check.loc[:, columns].values == df.loc[:, columns].values
            ndf_check[df.loc[:, columns].isna().values] = True
            if ndf_check.sum() == (ndf_check.shape[0] * ndf_check.shape[1]):
                is_insert = False
        if is_insert:
            db.insert_from_df(df, "tide_mst_genbo", n_round=0, is_select=True)
            db.execute_sql()
