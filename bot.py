import asyncio
import io
import os
from typing import Optional

import discord
from discord import app_commands

TOKEN = os.environ["DISCORD_TOKEN"]
OWNER_ID = int(os.environ["OWNER_ID"])  # your Discord user ID


class App(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()  # global sync; can take a few minutes to show up


client = App()


@client.tree.command(name="hi", description="Send a message several times")
@app_commands.describe(
    amount="Number of times to send the message (1-55)",
    text="The message to send",
    speed="Delay in seconds between messages (min 0.5, default 1.0)",
    photo="Attach an image",
    image_url="Link to an image",
)
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def hi(
    interaction: discord.Interaction,
    amount: app_commands.Range[int, 1, 55],
    text: str,
    speed: app_commands.Range[float, 0.5, 30.0] = 0.5,
    photo: Optional[discord.Attachment] = None,
    image_url: Optional[str] = None,
):
    # Owner-only
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            "This app is private.",
            ephemeral=True
        )
        return

    content = text

    if image_url and image_url.startswith(("http://", "https://")):
        content += f"\n{image_url}"

    photo_bytes = await photo.read() if photo else None

    def make_files():
        if photo_bytes:
            return [
                discord.File(
                    io.BytesIO(photo_bytes),
                    filename=photo.filename
                )
            ]
        return []

    await interaction.response.send_message("Sending...", ephemeral=True)

    channel = interaction.channel
    use_channel = channel is not None and interaction.guild is not None

    for i in range(amount):
        sent = False

        if use_channel:
            try:
                await channel.send(
                    content,
                    files=make_files()
                )
                sent = True
            except (discord.Forbidden, discord.HTTPException):
                use_channel = False

        if not sent:
            await interaction.followup.send(
                content,
                files=make_files()
            )

        if i < amount - 1:
            await asyncio.sleep(speed)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


client.run(TOKEN)
