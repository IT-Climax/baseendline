from flask import Flask, g
from .config import Config
from .db.async_core import init_async_db, app_specific_setup
from .api.resources import init_app
from .db.core import ma, jwt, cors, bcrypt, migrate

import asyncio


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    init_async_db(app)
    ma.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/*": {"origins": "*"}})
    bcrypt.init_app(app)
    migrate.init_app(app, None)  # None if using async

    # Async context for creating tables and preloading Excel questions
    async def async_setup():
        await app_specific_setup()  # This should create tables and preload questions

        # Run async setup synchronously at startup
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(app_specific_setup())
            loop.close()
        else:
            # If already running loop (e.g. in ASGI), schedule and wait
            loop.run_until_complete(app_specific_setup())

    init_app(app)

    @app.route('/')
    async def home():
        return {'message': 'Survey in Class API Running'}

    return app
