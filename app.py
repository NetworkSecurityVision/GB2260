from sanic import Sanic
from sanic.log import logger
from sanic.response import json, text
from sanic import Blueprint
from db import Database
import os

app = Sanic(__name__)

app.static('/static', './static')

@app.route('/status')
async def status(request):
    return text('ok')

# @app.route('/demo')
# async def demo(request):
#     return html('')

bp = Blueprint('division', url_prefix='/china/division/<year:2020>')


@bp.listener('before_server_start')
async def setup_connection(app, loop):
    global database
    database = Database()


@bp.listener('after_server_stop')
async def close_connection(app, loop):
    database.close()
    logger.info('server stopped')


@bp.route('/fuzzy')
async def test(request, year):
    return json({'hello': 'world'})


@bp.route('/area/<code:int>')
async def areas(request, year, code):
    """
    response type
    {
        code: 11,
        name: "北京市",
        parent: 0,
        fullpath: "北京市",
        location: {
            latitude: 116.405285,
            longitude: 39.904989,
            type: "GCJ02",
        }
        children: [
            {
                code: 1101,
                name: "北京市"
            }
        ]
    }
    """
    with_children = request.query_string.find('withChildren') > -1
    return json(database.areas(code, with_children))

@bp.route('/cities')
async def cities(request, year):
    return json([])

app.blueprint(bp)

port = os.getenv('PORT') or 5911
debug = os.getenv('DEBUG') == 'true'

app.run(host='0.0.0.0', port=int(port),
        debug=debug, workers=1, access_log=True)
