import argparse, folium
import pandas as pd
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
    parser.add_argument("--csv",  type=str)
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
    db       = DBConnector(args.host, port=args.port, dbname=args.db, user=args.user, password=args.pwd, dbtype="psgre", max_disp_len=200)
    df_mst_g = db.select_sql("select * from tide_mst_genbo  where created_date = (select max(created_date) from tide_mst_genbo );")
    df_mst_s = db.select_sql("select * from tide_mst_suisan where created_date = (select max(created_date) from tide_mst_suisan);")

    # location
    df_mst_g["latitude" ] = df_mst_g["latitude_degrees" ].astype(float) + df_mst_g["latitude_minutes" ].astype(float) / 60
    df_mst_g["longitude"] = df_mst_g["longitude_degrees"].astype(float) + df_mst_g["longitude_minutes"].astype(float) / 60
    df_mst_s = df_mst_s.loc[~df_mst_s["symbol"].isin(df_mst_g["symbol"]), :]
    df_mst_s["latitude" ] = df_mst_s["latitude_degrees" ].astype(float) + df_mst_s["latitude_minutes" ].astype(float) / 60
    df_mst_s["longitude"] = df_mst_s["longitude_degrees"].astype(float) + df_mst_s["longitude_minutes"].astype(float) / 60
    fmap = folium.Map(location=[df_mst_g["latitude"].median(), df_mst_g["longitude"].median()], zoom_start=8)
    for symbol, name, longitude, latitude in df_mst_g[["symbol", "name", "longitude", "latitude"]].values:
        folium.Marker(location=[latitude, longitude], popup=f"{symbol}: {name}", icon=folium.Icon(color='red')).add_to(fmap)
    for symbol, name, longitude, latitude in df_mst_s[["symbol", "name", "longitude", "latitude"]].values:
        folium.Marker(location=[latitude, longitude], popup=f"{symbol}: {name}", icon=folium.Icon(color='blue')).add_to(fmap)
    if args.csv is not None:
        df = pd.read_csv(args.csv)
        for name, longitude, latitude in df[["name", "longitude", "latitude"]].values:
            folium.Marker(location=[latitude, longitude], popup=f"{name}", icon=folium.Icon(color='orange')).add_to(fmap)
    fmap.save("map.html")
