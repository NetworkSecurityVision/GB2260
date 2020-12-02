# 数据库生成

下载数据

    git clone --depth 1 https://gitee.com/xiangyuecn/AreaCity-JsSpider-StatsGov.git

    git clone --depth 1 https://github.com/modood/Administrative-divisions-of-China.git

其中 拼音 和 坐标 数据来自 AreaCity-JsSpider-StatsGov 库，
坐标数据文件，前需要手动对该库数据进行格式修改。

1. 手动解压 data_geo.txt.7z 文件
2. 去掉开头的变量设置，使文件符合 json 格式，保存新文件，待处理

    sed 's/var DATA_GEO=//' data_geo.txt > data_geo.json

删除旧库

    rm ../data/2020/fuzzy.db

执行 Python 脚本

    python generate.cli.py
