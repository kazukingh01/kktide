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
    res = requests.get('https://www.data.jma.go.jp/kaiyou/db/tide/suisan/station.php')
    res.encoding = 'utf-8'
    soup    = bs4.BeautifulSoup(res.text, 'html.parser')
    table   = soup.find_all("table", attrs={"class": "data2"})[0]
    df      = []
    remarks = None
    for i, spwk in enumerate(table.find_all("tr")):
        if   i == 0: assert len(spwk.find_all("td")) == 0 and len(spwk.find_all("th")) == 11
        elif i == 1: assert len(spwk.find_all("td")) == 0 and len(spwk.find_all("th")) == 4
        elif i == 2: assert len(spwk.find_all("td")) == 0 and len(spwk.find_all("th")) == 8
        elif i == len(table.find_all("tr")) - 1:
            assert len(spwk.find_all("td")) == 1
            remarks = spwk.find_all("td")[0].text.strip()
        else:
            assert len(spwk.find_all("td")) == 18
            se = pd.Series(
                [x.text.strip() for x in spwk.find_all("td")],
                index=[
                    "place_no", "symbol", "name", "latitude", "longitude", "msl_above_st_min", "msl_above_tp", "st_min_above_tp", # st: spring tide 
                    "tide_m2_amp", "tide_m2_angle", "tide_s2_amp", "tide_s2_angle", "tide_k1_amp", "tide_k1_angle", "tide_o1_amp", "tide_o1_angle", 
                    "link", "remarks"
                ]
            )
            df.append(se)
    df = pd.concat(df, axis=1, ignore_index=False).T

    # Organize the data
    ## see: https://www.data.jma.go.jp/kaiyou/db/tide/suisan/explanation.html#station
    df["created_date"]      = datetime.datetime.now().strftime("%Y%m%d")
    df["place_no"]          = df["place_no"].astype(int)
    df["longitude_degrees"] = df["longitude"].str.split("゜").str[0].astype(int)
    df["longitude_minutes"] = df["longitude"].str.split("゜").str[1].str.split("'").str[0].astype(int)
    df["longitude_seconds"] = df["longitude"].str.split("゜").str[1].str.split("'").str[1].str.split('"').str[0].replace("", float("nan")).astype(float)
    df["latitude_degrees" ] = df["latitude" ].str.split("゜").str[0].astype(int)
    df["latitude_minutes" ] = df["latitude" ].str.split("゜").str[1].str.split("'").str[0].astype(int)
    df["latitude_seconds" ] = df["latitude" ].str.split("゜").str[1].str.split("'").str[1].str.split('"').str[0].replace("", float("nan")).astype(float)
    for x in ["msl_above_st_min", "msl_above_tp", "st_min_above_tp"]:
        df[f"{x}_mm"] = (df[x].replace("^-$", float("nan"), regex=True).astype(float) *  10).fillna(-1).astype(int).replace(-1, float("nan"))
    for x in ["tide_m2_amp", "tide_m2_angle", "tide_s2_amp", "tide_s2_angle", "tide_k1_amp", "tide_k1_angle", "tide_o1_amp", "tide_o1_angle"]:
        df[x] = (df[x].replace("^-$", float("nan"), regex=True).astype(float) * 100).fillna(-1).astype(int).replace(-1, float("nan")) / 100.
    df["remarks"]           = df["remarks"].map({re.split(r"\s", y)[0].strip():re.split(r"\s", y)[1].strip() for y in [x.strip() for x in remarks.split("\n")]})
    
    # to DB
    if args.update:
        db = Psgre(f"host={HOST} port={PORT} dbname={DBNAME} user={USER} password={PASS}", max_disp_len=200)
        df_check  = db.select_sql("select * from tide_mst_suisan where created_date = (select max(created_date) from tide_mst_suisan);")
        columns   = df_check.columns[1:-1]
        is_insert = True
        if df_check.shape[0] == df.shape[0]:
            ndf_check = df_check.loc[:, columns].values == df.loc[:, columns].values
            ndf_check[df.loc[:, columns].isna().values] = True
            if ndf_check.sum() == (ndf_check.shape[0] * ndf_check.shape[1]):
                is_insert = False
        if is_insert:
            db.insert_from_df(df, "tide_mst_suisan", n_round=2, is_select=True)
            db.execute_sql()
