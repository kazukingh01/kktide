import datetime, argparse
import requests
import pandas as pd
import numpy as np
from kkpsgre.connector import DBConnector
from kktide.util.com import load_module_from_file
from kklogger import set_logger


parser = argparse.ArgumentParser(
    description="This command get data, connect to database and upload. [Suisan]",
    epilog=r"""
    [kktidesuisan --load ~/kktide/config/config.py --year 202301 --since 200101 --update]
    """
)
parser.add_argument("--host", type=str)
parser.add_argument("--port", type=int)
parser.add_argument("--user", type=str)
parser.add_argument("--pwd",  type=str)
parser.add_argument("--db",   type=str)
parser.add_argument("--load", type=str)
parser.add_argument("--year",  type=str, help="--year  2023", required=True)
parser.add_argument("--since", type=str, help="--since 200101")
parser.add_argument("--update", action='store_true', default=False)
parser.add_argument("--csv", type=str)
args = parser.parse_args()
LOGGER = set_logger(__name__)


def suisan(args):
    LOGGER.info(f"{args}")
    if args.load is None:
        assert args.host is not None
        assert args.port is not None
        assert args.user is not None
        assert args.pwd  is not None
        assert args.db   is not None
    else:
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
    assert len(args.year) == 4
    if args.since is not None:
        assert len(args.since) == 4
        date_fr = datetime.datetime(int(args.since[:4]), 1, 1)
        date_to = datetime.datetime(int(args.year[ :4]), 1, 1)
        dates = sorted(list(set([datetime.datetime(x.year, 1, 1) for x in [date_fr + datetime.timedelta(days=i) for i in range((date_to - date_fr).days+1)] if x <= date_to])))
    else:
        dates = [datetime.datetime(int(args.year[:4]), 1, 1), ]

    # get master
    db     = DBConnector(args.host, port=args.port, dbname=args.db, user=args.user, password=args.pwd, dbtype="psgre", max_disp_len=200)
    df_mst = db.select_sql("select * from tide_mst_suisan where created_date = (select max(created_date) from tide_mst_suisan);")

    # Get data from TXT
    for date in dates:
        for symbol in df_mst["symbol"].values:
            url = f'https://www.data.jma.go.jp/kaiyou/data/db/tide/suisan/txt/{date.year}/{symbol}.txt'
            print(f"get data: {date}, {symbol}, {url}")
            res = requests.get(url)
            if res.status_code in [404]:
                print("invalid url.")
                continue
            df  = pd.DataFrame(res.text.split("\n"), columns=["txt"])
            df  = df.loc[df["txt"] != ""]
            if (df["txt"].str[0:3] == "   ").sum() == df.shape[0]:
                print("skip this symbol.")
                continue
            for h in range(24): df[h] = df["txt"].str[(3*h):(3*(h+1))].str.strip().replace("", float("nan")).astype(float)
            df["year"]  = df["txt"].str[3*24  :3*24+2].str.strip().astype(int)
            df["month"] = df["txt"].str[3*24+2:3*24+4].str.strip().astype(int)
            df["day"]   = df["txt"].str[3*24+4:3*24+6].str.strip().astype(int)
            for i in range(4):
                se = df["txt"].str[3*24+6+2+(7*i):3*24+6+2+(7*(i+1))]
                df[f"high_tide_time_hour_{i}"  ] = se.str[0:2].str.strip().replace("", float("nan")).astype(float)
                df[f"high_tide_time_minute_{i}"] = se.str[2:4].str.strip().replace("", float("nan")).astype(float)
                df[f"high_tide_level_{i}"      ] = se.str[4: ].str.strip().replace("", float("nan")).astype(float)
            for i in range(4):
                se = df["txt"].str[3*24+6+2+7*4+(7*i):3*24+6+2+7*4+(7*(i+1))]
                df[f"low_tide_time_hour_{i}"  ] = se.str[0:2].str.strip().replace("", float("nan")).astype(float)
                df[f"low_tide_time_minute_{i}"] = se.str[2:4].str.strip().replace("", float("nan")).astype(float)
                df[f"low_tide_level_{i}"      ] = se.str[4: ].str.strip().replace("", float("nan")).astype(float)
            list_ndf  = [np.concatenate([
                df.loc[:, ["year", "month", "day", i]].values,
                np.array([i] * df.shape[0]).reshape(-1, 1),
                np.array([0] * df.shape[0]).reshape(-1, 1),
                np.array([0] * df.shape[0]).reshape(-1, 1),
            ], axis=-1) for i in range(24)]
            list_ndf += [np.concatenate([
                df.loc[:, ["year", "month", "day", f"high_tide_level_{i}", f"high_tide_time_hour_{i}", f"high_tide_time_minute_{i}"]].values,
                np.array([1] * df.shape[0]).reshape(-1, 1),
            ], axis=-1) for i in range(4)]
            list_ndf += [np.concatenate([
                df.loc[:, ["year", "month", "day", f"low_tide_level_{i}", f"low_tide_time_hour_{i}", f"low_tide_time_minute_{i}"]].values,
                np.array([2] * df.shape[0]).reshape(-1, 1),
            ], axis=-1) for i in range(4)]
            df = pd.DataFrame(np.concatenate(list_ndf, axis=0), columns=["year", "month", "day", "level", "hour", "minute", "highlow"])
            df = df.loc[~(df["level"] >= 999) & ~(df["hour"].isna())]
            df[["year", "month", "day", "hour", "minute", "highlow"]] = df[["year", "month", "day", "hour", "minute", "highlow"]].astype(int)
            df["datetime"] = "20" + df["year"].astype(str).str.zfill(2) + df["month"].astype(str).str.zfill(2) + df["day"].astype(str).str.zfill(2) + df["hour"].astype(str).str.zfill(2) + df["minute"].astype(str).str.zfill(2) + "00"
            df["datetime"] = pd.to_datetime(df["datetime"])
            df["symbol"]   = symbol
            # to DB
            if args.update:
                db.set_sql(f"delete from tide_suisan where symbol = '{symbol}' and datetime >= '{str(df['datetime'].min())}' and datetime <= '{str(df['datetime'].max())}'")
                db.insert_from_df(df[["datetime", "symbol", "highlow", "level"]], "tide_suisan", n_round=0, is_select=False, set_sql=True)
                db.execute_sql()
            if args.csv is not None:
                df.to_csv(f"{args.csv}.{date.strftime('%Y%m')}.{symbol}.csv", index=False)


if __name__ == "__main__":
    suisan(args=args)
