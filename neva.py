import os
import sockjs
import serial
import asyncio
from aiohttp import web

SOCKJS_MNGR = 'chat'
ARDUINO_CORO = 'arduino_coro'
ARDUINO_PORT = 'arduino_port'

# ------------------------------------------------------------------------------
# correctly resolve static files
import sys
BASE_PATH = sys._MEIPASS \
    if hasattr(sys, '_MEIPASS') \
    else os.path.dirname(__file__)

# ------------------------------------------------------------------------------
# serve the app
def index(request):
    filepath = os.path.join(BASE_PATH, 'client/index.html')
    with open(filepath, 'rb') as file:
        return web.Response(body=file.read(), content_type='text/html')

# ------------------------------------------------------------------------------
# handle chat demo
def chat_msg_handler(msg, session):
    if msg.tp == sockjs.MSG_OPEN:
        session.manager.broadcast("Someone joined.")
    elif msg.tp == sockjs.MSG_MESSAGE:
        session.manager.broadcast(msg.data)
    elif msg.tp == sockjs.MSG_CLOSED:
        session.manager.broadcast("Someone left.")

# ------------------------------------------------------------------------------
# emit spam messages to all clients
@asyncio.coroutine
def spam_coro (app):
    try:
        while True:
            yield from asyncio.sleep(1.5)
            print('spam')
            sockjs.get_manager(SOCKJS_MNGR, app).broadcast('spam')
    except asyncio.CancelledError:
        pass

# ------------------------------------------------------------------------------
# serial port redirect
def arduino_readline(app):
    return app[ARDUINO_PORT].readline().decode()

@asyncio.coroutine
def arduino_coro(app):
    try:
        while True:
            line = yield from app.loop.run_in_executor(None, arduino_readline, app)
            print(line)
            sockjs.get_manager(SOCKJS_MNGR, app).broadcast(line)
    except asyncio.CancelledError:
        pass
    finally:
        app[ARDUINO_PORT].close()

# ------------------------------------------------------------------------------
# setup and teardown background tasks
@asyncio.coroutine
def start_background_tasks(app):
    # app['spam_coro'] = app.loop.create_task(spam_coro(app))
    app[ARDUINO_CORO] = app.loop.create_task(arduino_coro(app))


@asyncio.coroutine
def cleanup_background_tasks(app):
    # app['spam_coro'].cancel()
    app[ARDUINO_CORO].cancel()
    # yield from app['spam_coro']
    yield from app[ARDUINO_CORO]

# ------------------------------------------------------------------------------
# gracefully close all open socket connections on app shutdown
@asyncio.coroutine
def close_open_connections(app):
    mngr = sockjs.get_manager(SOCKJS_MNGR, app)
    yield from mngr.clear()
    mngr.stop()

# ------------------------------------------------------------------------------
# main
if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    # optional logging
    # ---
    # import logging
    # logging.basicConfig(level=logging.DEBUG,
    #                     format='%(asctime)s %(levelname)s %(message)s')

    # create web app - contains pseudo global variables
    app = web.Application(loop=loop)

    # add routes
    app.router.add_route('GET', '/', index)
    app.router.add_static('/assets', './client/assets')
    sockjs.add_endpoint(app, chat_msg_handler, name=SOCKJS_MNGR, prefix='/sockjs/')
    
    # add serial port connection
    app[ARDUINO_PORT] = serial.Serial('COM1', 9600)

    # bind lifecycle hooks
    app.on_startup.append(start_background_tasks)
    app.on_cleanup.append(cleanup_background_tasks)
    app.on_shutdown.append(close_open_connections)

    # kick off
    try:
        web.run_app(app)
        print("Server started at http://127.0.0.1:8080")
    except KeyboardInterrupt:
        pass
