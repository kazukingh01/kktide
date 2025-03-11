import bs4, re, datetime, argparse
import requests
import pandas as pd
from kkpsgre.connector import DBConnector
from kktide.util.com import load_module_from_file
from kklogger import set_logger


parser = argparse.ArgumentParser(
    description="This command get data, connect to database and upload. [GenboMst]",
    epilog=r"""
    [kktidegenbomst --update --load ~/kktide/config/config.py]
    [kktidegenbomst --update --host 172.17.0.2 --port 5432 --user postgres --pwd postgres --db tide]
    """
)
parser.add_argument("--host", type=str)
parser.add_argument("--port", type=int)
parser.add_argument("--user", type=str)
parser.add_argument("--pwd",  type=str)
parser.add_argument("--db",   type=str)
parser.add_argument("--load", type=str)
parser.add_argument("--update", action='store_true', default=False)
parser.add_argument("--csv", type=str)
args = parser.parse_args()
LOGGER = set_logger(__name__)


def genbo_mst(args=args):
    LOGGER.info(f"{args}")
    if args.load is not None:
        assert args.host is None
        assert args.port is None
        assert args.user is None
        assert args.pwd  is None
        assert args.db   is None
        spec = load_module_from_file(args.load)
        if hasattr(spec, "CONNECTION_STRING"):
            args.host = spec.CONNECTION_STRING
        else:
            args.host = spec.HOST
            args.port = spec.PORT
            args.user = spec.USER
            args.pwd  = spec.PASS
            args.db   = spec.DBNAME
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
        db        = DBConnector(args.host, port=args.port, dbname=args.db, user=args.user, password=args.pwd, dbtype="psgre", max_disp_len=200)
        df_check  = db.select_sql("select * from tide_mst_genbo where created_date = (select max(created_date) from tide_mst_genbo);")
        columns   = df_check.columns[1:-1]
        is_insert = True
        if df_check.shape[0] == df.shape[0]:
            dfwk1 = df.      loc[:, columns].set_index("symbol").copy()
            dfwk2 = df_check.loc[:, columns].set_index("symbol").copy()
            dfwk1 = dfwk1.loc[dfwk2.index].replace(float("nan"), None)
            dfwk2 = dfwk2.replace(float("nan"), None)
            if (dfwk1.to_numpy(dtype=object) != dfwk2.to_numpy(dtype=object)).sum() == 0:
                is_insert = False
            else:
                is_insert = True
                assert df["created_date"].max() > df_check["created_date"].max()
        if is_insert:
            db.insert_from_df(df, "tide_mst_genbo", n_round=0, is_select=True)
            db.execute_sql()
        else:
            LOGGER.warning("All data is already in the database.")
    if args.csv is not None:
        df.to_csv(args.csv, index=False)
    return df


if __name__ == "__main__":
    df = genbo_mst(args=args)
