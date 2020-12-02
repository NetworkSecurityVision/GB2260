# China Administrative Division

## Why

提供统一标准的（GB2260）中国行政区划数据。包括省、市、区县、村镇的名称、拼音、编号、地理坐标信息。

1. 统一行政区划标准，地区名称和地区编号均采用国标，并在国家行政区划发生变化时，支持不同版本。
2. 提供统一接口，同时面向其它服务（前端、后端）提供统一接口。
3. 其它快捷功能，地区层级关系、模糊搜索等。

## Start Server

```shell
pip3 install -r requirements.txt
python3 app.py
```

## Design

-   Python https://www.python.org/
-   Sanic https://sanicframework.org/
-   ## Sqlite3 https://www.sqlite.org/index.html
    -   fuzzy search https://www.sqlite.org/fts3.html
-   Docker https://docker.com/

## Data Source

数据源

-   https://github.com/modood/Administrative-divisions-of-China
-   https://github.com/xiangyuecn/AreaCity-JsSpider-StatsGov

**行政区划标准说明**

中国行政区划由**民政部**负责维护、更新（惯例上会每年发布一次），
目前最新版是 2020 年第七次人口普查期间使用的版本，
数据格式采用 GB/T 2260 标准，每一个行政区划都有自己的唯一编号（[编号含义](http://www.stats.gov.cn/tjsj/tjbz/200911/t20091125_8667.html)）。

## API

#### 模糊搜索

    GET /china/division/fuzzy?k=xxx

返回数据

```json
[
    {
        "code": "",
        "name": "",
        "fullpath": ""
    }
]
```

#### 行政地区详情

    GET /china/division/:id?withChildren

返回数据

```json
{
    "code": 1000,
    "name": "海淀区",
    "fullpath": ["北京市", "北京", "海淀区"],
    "WGS84": {
        "latitide": 0,
        "longitude": 0
    },
    "children": [{ "code": "100010", "name": "" }]
}
```
