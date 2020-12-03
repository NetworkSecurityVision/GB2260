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


def read_raw_data():
    def readfile(
        filename,
        code_field=False,
        with_children=True,
    ):
        with open(filename, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                parent = row[code_field] if code_field else "0"
                data[parent]["children"].append(row["code"])
                data[row["code"]] = {
                    "fullname": row["name"],
                    "name": row["name"],
                }
                if with_children:
                    data[row["code"]]["children"] = []

    readfile("./Administrative-divisions-of-China/dist/provinces.csv")
    readfile("./Administrative-divisions-of-China/dist/cities.csv", "provinceCode")
    readfile("./Administrative-divisions-of-China/dist/areas.csv", "cityCode")
    readfile(
        "./Administrative-divisions-of-China/dist/streets.csv",
        "areaCode",
        with_children=False,
    )


def read_pinyin():
    with open(
        "./AreaCity-JsSpider-StatsGov/src/采集到的数据/ok_data_level4.csv",
        "r",
        encoding="utf_8_sig",
    ) as f:
        reader = csv.DictReader(f)
        # id,pid,deep,name,pinyin_prefix,pinyin,ext_id,ext_name
        for row in reader:
            try:
                area = data[row["id"]]
                area["pinyin"] = row["pinyin"]
                area["name"] = row["name"]
            except KeyError:
                print("跳过非标准地区：(%s) %s" % (row["id"], row["ext_name"]))
                pass


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
                pass


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
        pinyin = (
            " ".join(list("".join(v["pinyin"].split(" ")))) if v.get("pinyin") else ""
        )
        cursor.execute(
            """
        insert into divisions (code, pinyin, name) values ('%s', '%s', '%s')
        """
            % (k, pinyin, name)
        )

    # 优化 fts4 索引
    cursor.execute("INSERT INTO divisions(divisions) VALUES('optimize')")
    conn.commit()


def mark_direct_area():
    """
    标记处直辖行政区划，直辖地区不是一个真实的行政区划，而是一个虚拟的等级，
    直辖有两种：直辖市、直辖区县，占据对应规划层级但并没有真实地区。
    """
    # 直辖市：北京，天津，上海，重庆
    # 市辖区县：  河南、湖北、海南、重庆、新疆
    areas = [
        "1101",
        "1201",
        "3101",
        "5001",
        "4190",
        "4290",
        "4690",
        "5001",
        "5002",
        "6590",
    ]

    for i in areas:
        data[i]["is_direct"] = True


def supplement():
    """
    补充港澳台数据
    """
    data["71"] = {
        "fullname": "台湾省",
        "name": "台湾",
        "pinyin": "tai wan",
        "fullpath": "台湾省",
    }
    data["81"] = {
        "fullname": "香港特别行政区",
        "name": "香港",
        "pinyin": "xiang gang",
        "fullpath": "香港特别行政区",
    }
    data["82"] = {
        "fullname": "澳门特别行政区",
        "name": "澳门",
        "pinyin": "ao men",
        "fullpath": "澳门特别行政区",
    }
    data["0"]["children"].extend(["71", "81", "82"])


read_raw_data()
mark_direct_area()
supplement()
read_pinyin()
read_geo()

dumpf = open(DATA_PATH, "w")
json.dump(data, dumpf, ensure_ascii=False, indent=True)

create_fuzzy_db()