import csv
import sqlite3
import json
import os


data = {
    "0": {
        "name": "中国",
        "location": {"lat": 39.904989, "lng": 116.405285, "type": "GCJ02"},
        "children": [],
    }
}

DB_PATH = "../data/2020/fuzzy.db"
DATA_PATH = "../data/2020/data.json"


def read_provinces():
    with open("./Administrative-divisions-of-China/dist/provinces.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data[row["code"]] = {"name": row["name"], "children": []}
            data["0"]["children"].append(row["code"])


def read_cities():
    with open("./Administrative-divisions-of-China/dist/cities.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data[row["provinceCode"]]["children"].append(row["code"])
            data[row["code"]] = {"name": row["name"], "children": []}


def read_areas():
    with open("./Administrative-divisions-of-China/dist/areas.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data[row["cityCode"]]["children"].append(row["code"])
            data[row["code"]] = {"name": row["name"], "children": []}


def read_streets():
    with open("./Administrative-divisions-of-China/dist/streets.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data[row["areaCode"]]["children"].append(row["code"])
            data[row["code"]] = {"name": row["name"], "children": []}


def read_pinyin():
    with open(
        "./AreaCity-JsSpider-StatsGov/src/采集到的数据/ok_data_level4.csv",
        "r",
        encoding="utf_8_sig",
    ) as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                data[row["id"]]["pinyin"] = row["pinyin"]
            except KeyError:
                print("跳过非标准地区：(%s) %s" % (row["id"], row["ext_name"] or row["name"]))


def read_geo():
    with open(
        "./AreaCity-JsSpider-StatsGov/src/采集到的数据/data_geo.json",
        "r",
        encoding="utf_8_sig",
    ) as f:
        cnt = json.load(f)
        for row in cnt:
            if str(row["id"]).startswith("71"):
                continue
            lng, lat = row["geo"].split(" ")
            try:
                data[str(row["id"])]["location"] = {
                    "lat": float(lat),
                    "lng": float(lng),
                    "type": "GCJ02",  # 国家测绘局坐标系
                }
            except KeyError:
                print("跳过，非标准地区坐标: (%s) %s" % (row["id"], row["ext_path"]))


def create_fuzzy_db():

    try:
        os.remove(DB_PATH)
    except FileNotFoundError:
        pass

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
create virtual table divisions using fts4(code, pinyin, name)
        """
    )
    conn.commit()

    for (k, v) in data.items():
        name = " ".join(list(v["name"]))
        pinyin = " ".join(list("".join(v["pinyin"].split(" ")))) if v.get('pinyin') else ''
        cursor.execute(
            """
        insert into divisions (code, pinyin, name) values ('%s', '%s', '%s')
        """
            % (k, pinyin, name)
        )

    # 优化 fts4 索引
    cursor.execute("INSERT INTO divisions(divisions) VALUES('optimize')")
    conn.commit()


read_provinces()
read_cities()
read_areas()
read_streets()
read_geo()

dumpf = open(DATA_PATH, "w")
json.dump(data, dumpf, ensure_ascii=False, indent=True)

read_pinyin()
create_fuzzy_db()