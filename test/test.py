import argparse
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from kkpsgre.connector import DBConnector
from kktide.util.com import load_module_from_file


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str)
    parser.add_argument("--port", type=int)
    parser.add_argument("--user", type=str)
    parser.add_argument("--pwd",  type=str)
    parser.add_argument("--db",   type=str)
    parser.add_argument("--load", type=str)    
    args = parser.parse_args()
    print(args)
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
    db = DBConnector(args.host, port=args.port, dbname=args.db, user=args.user, password=args.pwd, dbtype="psgre", max_disp_len=200)
    df = db.select_sql("SELECT datetime, symbol, highlow, level FROM tide_suisan WHERE symbol = 'TK' and datetime >= '2024-02-02 00:00:00' and datetime < '2024-02-03 00:00:00';")
    df["datetime"] = pd.to_datetime(df["datetime"])
    df["datetime"] = df["datetime"].astype(int) // (10 ** 9)
    df_time = pd.DataFrame(np.arange(df["datetime"].min(), df["datetime"].max() + 60, 60), columns=["datetime"])
    df_time = pd.merge(df_time, df, how="left", on="datetime")
    df_time["level"] = df_time["level"].interpolate()
    y_fft   = np.fft.fft(df_time["level"])
    amp     = 1 / y_fft.shape[0] * y_fft.real #This gives wrong results
    indexes = np.argsort(amp)[np.arange(0, amp.shape[0], 2)]
    y_ifft  = np.fft.ifft(y_fft[indexes], n=y_fft.shape[0])
    fig, ax = plt.subplots(figsize=(12,8))
    ax.plot(pd.to_datetime(df_time["datetime"] * (10 ** 9)), y_ifft.real,      color="r", label="fft")
    ax.plot(pd.to_datetime(df_time["datetime"] * (10 ** 9)), df_time["level"], color="b", label="gt")
    ax.legend()
    fig.show()
