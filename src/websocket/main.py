import aiohttp
import asyncio
import json
import os
from src.utils.console import Console
from src.handlers.monitor import Monitor

class WebSocket:
    def __init__(self):
        self.uri = f"ws://{os.getenv('WEBSOCKET_HOST')}/{os.getenv('WEBSOCKET_PATH')}"
        self.ws = None
        self._session = None
        self._reconnect_interval = 5
        self._running = False
        self.monitor = None

    async def start(self):
        self._running = True
        
        if not self._session or self._session.closed:
            self._session = aiohttp.ClientSession()

        while self._running:
            try:                
                async with self._session.ws_connect(self.uri, heartbeat=30.0) as ws:
                    self.ws = ws                    
                    await self.on_connect()

                    async for msg in ws:
                        if not self._running:
                            break
                            
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            try:
                                await self._handle_raw_message(msg.data)
                            except Exception as e:
                                Console.error(f"Error handling message: {e}", module="WEBSOCKET")
                        elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.CLOSING):
                            Console.warning("WebSocket closing or closed by server", module="WEBSOCKET")
                            break
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            Console.error(f"WebSocket experienced an error: {ws.exception()}", module="WEBSOCKET")
                            break
                    
                    await self.on_disconnect()

            except aiohttp.ClientConnectorError:
                Console.error(f"Connection failed: Server at {self.uri} is unreachable.", module="WEBSOCKET")
            except Exception as e:
                Console.error(f"Unexpected error in websocket loop: {e}", module="WEBSOCKET")

            if self._running:
                Console.info(f"Retrying connection in {self._reconnect_interval}s...", module="WEBSOCKET")
                await asyncio.sleep(self._reconnect_interval)

    async def _handle_raw_message(self, data: str):
        try:
            payload = json.loads(data)

            await self.monitor.websocketMessage(payload)
            await self.on_message(payload)
        except json.JSONDecodeError:
            Console.warning(f"Received non-JSON payload: {data[:100]}...", module="WEBSOCKET")

    async def on_message(self, last_payload: dict):
        #Console.debug(f"Received message: {last_payload}", module="WEBSOCKET")
        pass

    async def send(self, data: dict):
        if self.ws and not self.ws.closed:
            try:
                await self.ws.send_json(data)
                Console.debug(f"Message sent: {data}", module="WEBSOCKET")
            except Exception as e:
                Console.error(f"Failed to send data: {e}", module="WEBSOCKET")
        else:
            Console.warning("Attempted to send message while disconnected", module="WEBSOCKET")

    async def on_connect(self):
        pass

    async def on_disconnect(self):
        self.ws = None

    async def stop(self):
        self._running = False
        if self.ws:
            await self.ws.close()
        if self._session:
            await self._session.close()
        Console.info("Closed WebSocket connection successfully", module="WEBSOCKET")
