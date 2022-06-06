##-----------------------------------##
#  IMPORTS
##-----------------------------------##

# IMPORT DISCORD.PY. ALLOWS ACCESS TO DISCORD'S API.
import discord
from discord.ext import tasks

# IMPORT THE OS MODULE.
import os

# IMPORT LOAD_DOTENV FUNCTION FROM DOTENV MODULE.
from dotenv import load_dotenv

# IMPORT API CALL MODULE - REQUESTS.
import requests

# IMPORT PANDAS WITH JSON.
import pandas as pd
from pandas.io.json import json_normalize

##-----------------------------------##
#  SETUP
##-----------------------------------##

# LOADS THE .ENV FILE THAT RESIDES ON THE SAME LEVEL AS THE SCRIPT.
load_dotenv()

# GRAB THE API TOKEN FROM THE .ENV FILE.
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# GETS THE CLIENT OBJECT FROM DISCORD.PY. CLIENT IS SYNONYMOUS WITH BOT.
bot = discord.Client()

# API CALL WEBSITE ADDRESS FROM BITTREX
url= 'https://bittrex.com/api/v2.0/pub/currencies/GetWalletHealth'

##-----------------------------------##
#  LISTENERS
##-----------------------------------##

# EVENT LISTENER FOR WHEN THE BOT HAS SWITCHED FROM OFFLINE TO ONLINE.
@bot.event
async def on_ready():
	# CREATES A COUNTER TO KEEP TRACK OF HOW MANY GUILDS / SERVERS THE BOT IS CONNECTED TO.
	guild_count = 0

	# LOOPS THROUGH ALL THE GUILD / SERVERS THAT THE BOT IS ASSOCIATED WITH.
	for guild in bot.guilds:
		# PRINT THE SERVER'S ID AND NAME.
		print(f"- {guild.id} (name: {guild.name})")

		# INCREMENTS THE GUILD COUNTER.
		guild_count = guild_count + 1

	# PRINTS HOW MANY GUILDS / SERVERS THE BOT IS IN.
	channel = bot.get_channel(978487447254085635)
	empty_wallet = pd.DataFrame(columns=['currency', 'pw', 'cw']).set_index('currency')
	print("SampleDiscordBot is in " + str(guild_count) + " guilds.")
	print(channel)
	myLoop.start(channel, empty_wallet)

# EVENT LISTENER FOR WHEN A NEW MESSAGE IS SENT TO A CHANNEL.
@bot.event
async def on_message(message):
	# BOT INTEREACTION TO TURN ON AND OFF REMOTELY.
	if message.content == "pause":
		await message.channel.send("PAUSED!")
		myLoop.cancel()
	# LISTEN FOR 'start' TO START LOOP
	elif message.content == "start":
		await message.channel.send("RUNNING!")
		channel = bot.get_channel(978487447254085635)
		empty_wallet = pd.DataFrame(columns=['currency', 'pw', 'cw']).set_index('currency')
		myLoop.start(channel, empty_wallet)
	# LISTEN FOR 'status' TO RETURN INSTANT STATUS OF WALLETS
	elif message.content == "status":
		# CURRENT STATE OF BITTRECT WALLETS API CALL
		current_wallet = pd.DataFrame.from_dict(json_normalize(requests.get(url).json()['result']), orient='columns')
		cw = current_wallet[['Health.Currency', 'Health.IsActive']].rename(columns={'Health.Currency':'currency', 'Health.IsActive':'isactive'}).set_index('currency')
		await message.channel.send(cw)

##-----------------------------------##
#  MAIN LOOP FOR CHECKING STOCKS
##-----------------------------------##

@tasks.loop(seconds = 30) # repeat after every 30 seconds
async def myLoop(channel, wallet):
	# CURRENT STATE OF BITTRECT WALLETS API CALL
	current_wallet = pd.DataFrame.from_dict(json_normalize(requests.get(url).json()['result']), orient='columns')
	cw = current_wallet[['Health.Currency', 'Health.IsActive']].rename(columns={'Health.Currency':'currency', 'Health.IsActive':'isactive'}).set_index('currency')
	wallet['cw']=cw

	# TEST FOR CHANGE BETWEEN CURRENT WALLET STATUS AND PREVIOUS WALLET.
	wallet['change'] = wallet['cw'] != wallet['pw']
	
	# BUILD MESSAGE ARRAY
	mess = []
	for index, row in wallet.iterrows():
		if row['change']:
			mess.append(index + ' ' + str(row['cw']))
			
	# MESSAGE MAXIMUM 20
	if len(mess) > 20:
		await channel.send('overflow')
	elif mess:    
		await channel.send(mess)
	wallet['pw']=cw

# EXECUTES THE BOT WITH THE SPECIFIED TOKEN.
bot.run(DISCORD_TOKEN)
