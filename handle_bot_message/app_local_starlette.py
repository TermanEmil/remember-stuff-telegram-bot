import asyncio
import logging
import os

import uvicorn
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route
from telegram import Update
from telegram.ext import (
    Application,
    filters, MessageHandler
)

from update_handler import handle_update

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Set up the application and a custom webserver."""
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    url = os.environ.get("NGROK_WEBSERVER_URL")

    application = Application.builder().token(bot_token).updater(None).build()
    application.add_handler(MessageHandler(filters.ALL, handle_update))
    await application.bot.set_webhook(url=f"{url}/telegram")

    # Set up webserver
    async def telegram_endpoint(request: Request) -> Response:
        """Handle incoming Telegram updates by putting them into the `update_queue`"""
        await application.update_queue.put(
            Update.de_json(data=await request.json(), bot=application.bot)
        )
        return Response()

    middleware = [
        Middleware(CORSMiddleware, allow_origins=['*'])
    ]

    starlette_app = Starlette(
        routes=[
            Route("/telegram", telegram_endpoint, methods=["POST"]),
        ],
        middleware=middleware
    )
    webserver = uvicorn.Server(
        config=uvicorn.Config(
            app=starlette_app,
            port=5000,
            use_colors=False,
            host="127.0.0.1",
        )
    )

    # Run application and webserver together
    async with application:
        await application.start()
        await webserver.serve()
        await application.stop()


if __name__ == "__main__":
    asyncio.run(main())
