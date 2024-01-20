import datetime, argparse, math
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
from kkpsgre.psgre import Psgre
from kktide.config.psgre import HOST, PORT, USER, PASS, DBNAME
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

font_path   = './ipaexg.ttf'
ipaexg_font = FontProperties(fname=font_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fr",   type=str, help="--fr 20230101")
    parser.add_argument("--to",   type=str, help="--to 20230101")
    parser.add_argument("--list", action='store_true', default=False)
    parser.add_argument("--s",    type=str, help="--s MT,TA", default="")
    parser.add_argument("--genbo",  action='store_true', default=False)
    parser.add_argument("--suisan", action='store_true', default=False)
    args = parser.parse_args()
    assert args.genbo + args.suisan < 2
    db       = Psgre(f"host={HOST} port={PORT} dbname={DBNAME} user={USER} password={PASS}", max_disp_len=200)
    df_mst_g = db.select_sql("select * from tide_mst_genbo  where created_date = (select max(created_date) from tide_mst_genbo );")
    df_mst_s = db.select_sql("select * from tide_mst_suisan where created_date = (select max(created_date) from tide_mst_suisan);")
    dict_mst_g = {x: y for x, y in df_mst_g[["symbol", "name"]].values}
    dict_mst_s = {x: y for x, y in df_mst_s[["symbol", "name"]].values}
    if args.list:
        print("========== tide_mst_genbo ==========")
        print(dict_mst_g)
        print("========== tide_mst_suisan ==========")
        print(dict_mst_s)
    else:
        try:
            symbols = int(args.s)
            symbols = np.array(list(dict_mst_g.keys()))[np.random.permutation(np.arange(len(dict_mst_g)))[:symbols]].tolist()
        except ValueError:
            symbols = args.s.split(",")
            for x in symbols: assert (x in list(dict_mst_g.keys()) or x in list(dict_mst_s.keys()))
        assert len(args.fr) == 8
        assert len(args.to) == 8
        date_from = datetime.datetime.fromisoformat(args.fr)
        date_to   = datetime.datetime.fromisoformat(args.to) + datetime.timedelta(days=1)
        df_g      = db.select_sql(f"select * from tide_genbo  where symbol in ('" + "','".join(symbols) + f"') and datetime >= '{str(date_from)}' and datetime < '{str(date_to)}';")
        df_s      = db.select_sql(f"select * from tide_suisan where symbol in ('" + "','".join(symbols) + f"') and datetime >= '{str(date_from)}' and datetime < '{str(date_to)}';")
        df_g      = df_g.sort_values(["symbol", "datetime", "highlow"]).reset_index(drop=True)
        df_s      = df_s.sort_values(["symbol", "datetime", "highlow"]).reset_index(drop=True)
        ndf1      = np.array([date_from + datetime.timedelta(hours=i) for i in range(int((date_to - date_from).total_seconds() // (60 * 60)) + 1)])
        ndf2      = np.array(symbols)
        df_base   = pd.DataFrame(np.stack([np.tile(ndf1, ndf2.shape[0]), np.array(symbols).repeat(ndf1.shape[0])]).T, columns=["datetime", "symbol"])
        df_gd     = pd.merge(df_base, df_g.loc[df_g["highlow"] == 0], how="left", on=["datetime", "symbol"])
        df_sd     = pd.merge(df_base, df_s.loc[df_s["highlow"] == 0], how="left", on=["datetime", "symbol"])
        df_gd["prev"] = df_gd.groupby("symbol", group_keys=False)["level"].shift(1)
        df_sd["prev"] = df_sd.groupby("symbol", group_keys=False)["level"].shift(1)
        df_gd["diff"] = df_gd["level"] - df_gd["prev"]
        df_sd["diff"] = df_sd["level"] - df_sd["prev"]
        df_d          = df_gd[["datetime", "symbol", "highlow"]].copy()
        df_d["diff"]  = df_gd["diff"] - df_sd["diff"]
        nv      = int(len(symbols) ** (1/2))
        nh      = math.ceil(len(symbols) ** (1/2))
        fig, ax = plt.subplots(nv + (1 if (nv * nh) < len(symbols) else 0), nh, figsize=(15, 9))
        ax      = ax.flatten() if hasattr(ax, "flatten") else np.array([ax])
        ax      = {y:x for x, y in zip(ax, symbols)}
        colors  = {x: ["r", "g", "b", "c", "m", "y", "k", "w"][i % 8] for i, x in enumerate(symbols)}
        for df, colname, str_gs in zip([df_g, df_s, df_gd, df_sd, df_d], ["level", "level", "diff", "diff", "diff"], ["g_level", "s_level", "g_diff", "s_diff", "diff_g-s"]):
            for (symbol, highlow), dfwk in df.groupby(["symbol", "highlow"]):
                if args.genbo  and str_gs[0] == "s": continue
                if args.suisan and str_gs[0] == "g": continue
                if highlow == 0: ax[symbol].plot(   dfwk.loc[~dfwk[colname].isna(), "datetime"], dfwk.loc[~dfwk[colname].isna(), colname], color=colors[symbol], linestyle={"g_level": "--", "s_level": ":", "g_diff": "--", "s_diff": ":", "diff_g-s": "-"}[str_gs], label=f"{str_gs}: {symbol} {dict_mst_s[symbol]}")
                if highlow == 1: ax[symbol].scatter(dfwk.loc[~dfwk[colname].isna(), "datetime"], dfwk.loc[~dfwk[colname].isna(), colname], color=colors[symbol], marker={"g_level": "*", "s_level": "^"}[str_gs])
                if highlow == 2: ax[symbol].scatter(dfwk.loc[~dfwk[colname].isna(), "datetime"], dfwk.loc[~dfwk[colname].isna(), colname], color=colors[symbol], marker={"g_level": "o", "s_level": "v"}[str_gs])
        for _, x in ax.items(): x.legend(prop=ipaexg_font)
        fig.autofmt_xdate()
        fig.show()
        fig, ax = plt.subplots(1, 1, figsize=(15, 9))
        for df, colname, str_gs in zip([df_gd, df_sd, df_d], ["diff", "diff", "diff"], ["g_diff", "s_diff", "diff_g-s"]):
            for (symbol, highlow), dfwk in df.groupby(["symbol", "highlow"]):
                if args.genbo  and str_gs[0] == "s": continue
                if args.suisan and str_gs[0] == "g": continue
                if highlow == 0: ax.plot(   dfwk.loc[~dfwk[colname].isna(), "datetime"], dfwk.loc[~dfwk[colname].isna(), colname], color=colors[symbol], linestyle={"g_level": "--", "s_level": ":", "g_diff": "--", "s_diff": ":", "diff_g-s": "-"}[str_gs], label=f"{str_gs}: {symbol} {dict_mst_s[symbol]}")
                if highlow == 1: ax.scatter(dfwk.loc[~dfwk[colname].isna(), "datetime"], dfwk.loc[~dfwk[colname].isna(), colname], color=colors[symbol], marker={"g_level": "*", "s_level": "^"}[str_gs])
                if highlow == 2: ax.scatter(dfwk.loc[~dfwk[colname].isna(), "datetime"], dfwk.loc[~dfwk[colname].isna(), colname], color=colors[symbol], marker={"g_level": "o", "s_level": "v"}[str_gs])
        ax.legend(prop=ipaexg_font)
        fig.autofmt_xdate()
        fig.show()

