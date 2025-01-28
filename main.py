import discord
from discord import app_commands
from discord.ext import commands
import subprocess
import json
import os

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.mentions = True
        super().__init__(command_prefix="!", intents=intents)
        self.current_model = "gpt-3.5-turbo"  # Default model

    async def setup_hook(self):
        await self.tree.sync()

bot = Bot()

def get_ai_response(prompt, model):
    curl_command = f'''curl -X POST "https://api.khumbuicefall.com/v1/chat/completions" -H "Content-Type: application/json" -d '{{"model": "{model}", "messages": [{{"role": "user", "content": "{prompt}"}}], "temperature": 0.7}}\''''
    
    try:
        response = subprocess.check_output(curl_command, shell=True)
        response_data = json.loads(response)
        return response_data['choices'][0]['message']['content']
    except Exception as e:
        return f"Error: {str(e)}"

@bot.event
async def on_ready():
    print(f'Bot is ready: {bot.user.name}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user in message.mentions:
        question = message.content.replace(f'<@{bot.user.id}>', '').strip()
        
        if question:
            async with message.channel.typing():
                response = get_ai_response(question, bot.current_model)
                await message.reply(f"**Using Model:** {bot.current_model}\n\n{response}")

    await bot.process_commands(message)

@bot.tree.command(name="setmodel", description="Set the default AI model for @ mentions")
@app_commands.describe(model="Choose the AI model to use")
@app_commands.choices(model=[
    app_commands.Choice(name="GPT-3.5", value="gpt-3.5-turbo"),
    app_commands.Choice(name="GPT-4", value="gpt-4"),
    app_commands.Choice(name="Claude-2", value="claude-2"),
    app_commands.Choice(name="PaLM-2", value="palm-2"),
    app_commands.Choice(name="Llama-2", value="llama-2-70b")
])
async def setmodel(interaction: discord.Interaction, model: str):
    bot.current_model = model
    await interaction.response.send_message(f"Default model set to: {model}")

@bot.tree.command(name="currentmodel", description="Show the current default model")
async def currentmodel(interaction: discord.Interaction):
    await interaction.response.send_message(f"Current default model is: {bot.current_model}")

# Start the bot
bot.run(os.getenv('TOKEN'))
