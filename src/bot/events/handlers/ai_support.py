import os
import json
import aiohttp
import discord
import asyncio
from discord.ext import commands
from src.utils.console import Console

class AISupport(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.prompt = self.__load_prompt()

    def __load_prompt(self):
        path = os.path.join("data", "ai_support", "prompt.txt")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read().strip()
        else:
            Console.error("An error occurred while loading the prompt: No prompt found", "AI_SUPPORT")
            return None

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
            
        if message.guild.id != int(os.getenv("MAIN_GUILD", 0)):
            return
        
        configPath = os.path.join("data", "ai_support", "config.json")
        if not os.path.exists(configPath): return

        def load_ai_config():
            with open(configPath, 'r', encoding='utf-8') as file:
                return json.load(file)
                
        data = await asyncio.to_thread(load_ai_config)
        if message.channel.id not in data.get("channels", []):
            return

        text = (message.content or "").strip()
        api_key = os.getenv("OPENAI_TOKEN", "").strip()
        if not text or not api_key:
            return
        try:
            async with message.channel.typing():
                # Process conversation context
                history = []
                async for m in message.channel.history(limit=10, oldest_first=False):                
                    # Skip other bots, keep assistant and users
                    if m.author.bot and m.author.id != self.bot.user.id:
                        continue
                    
                    content = (m.content or "").strip()
                    if content and m.id != message.id: # Don't include the current message in the history yet
                        history.insert(0, {
                            "role": "assistant" if m.author.id == self.bot.user.id else "user", 
                            "content": content
                        })
                
                # Always append the current message as the final user prompt
                history.append({"role": "user", "content": text})
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        os.getenv("OPENAI_URI", "https://api.openai.com/v1/chat/completions"),
                        headers={
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip(),
                            "messages": [{"role": "system", "content": self.prompt}] + history[-11:],
                            "temperature": 0.7,
                            "max_tokens": 1000,
                        }
                    ) as resp:
                        if resp.status != 200:
                            Console.error(f"AI process failed: {resp.status}", "AI_SUPPORT")
                            return
                        
                        data = await resp.json()
                        result = data["choices"][0]["message"]["content"] if data["choices"] else "An error occurred while generating a response."
                        
                        chunks = [result[i : i + 1900] for i in range(0, len(result), 1900)]
                        for i, chunk in enumerate(chunks):
                            if i == 0:
                                await message.reply(chunk, mention_author=False)
                            else:
                                await message.channel.send(chunk)
        except Exception as e:
            Console.error(f"AI process failed: {e}", "AI_SUPPORT")

