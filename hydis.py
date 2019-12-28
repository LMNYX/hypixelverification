import discord
import sqlite3
from colorama import init, Fore, Back
import requests
import json
init(autoreset=True)

users = sqlite3.connect("users.db")
u = users.cursor()

u.execute("CREATE TABLE IF NOT EXISTS users (discordId text, minecraftUsername text)")
users.commit()
HYPIXEL_TOKEN = ""
DISCORD_TOKEN = ""

client = discord.Client()

@client.event
async def on_ready():
	print('Logged in as '+Fore.CYAN+'{0.user}'.format(client))
	await client.change_presence(status= discord.Status.dnd, activity=discord.Activity(application_id=0, name="thirtyvirus' video", type=discord.ActivityType.watching))

@client.event
async def on_message(message):
	if message.author == client.user:
		return
	if message.content.startswith('h!fork'):
		await message.author.send("https://github.com/lmnyx/hypixelverification")
		await message.delete()
	if(message.content.startswith('h!get')):
		args = message.content.split(' ')
		del args[0]
		if(len(args) < 1 or len(args) > 1):
			await message.channel.send('❌ Mention user as argument!')
			return
		if(len(message.mentions) < 1):
			await message.channel.send('❌ Mention user as argument!')
			return
		checka = u.execute("SELECT * FROM users WHERE discordId = '{0}'".format(str(message.mentions[0].id)))
		d = u.fetchone()
		if(len(d) == 0):
			await message.channel.send('❌ This user didn\'t linked any Minecraft account yet!')
			return
		await message.channel.send('✅ {0}#{1}\'s Minecraft IGN is `{2}`'.format(message.mentions[0].name, str(message.mentions[0].discriminator), d[1]))
		return
	if message.content.startswith('h!verify'):
		args = message.content.split(' ')
		del args[0]
		if(len(args) < 1):
			await message.channel.send('❌ Provide Minecraft IGN as argument!\nExample: `h!verify lmnyx`')
		elif(len(args) > 1):
			await message.channel.send('❌ Provide Minecraft IGN as argument!\nExample: `h!verify lmnyx`')
		else:
			chm = await message.channel.send('Checking the `{0}`...'.format(args[0]))
			userinfo = json.loads(requests.get("https://api.hypixel.net/player?key={0}&name={1}".format(HYPIXEL_TOKEN, args[0])).content)
			if(userinfo['player'] == None):
				await chm.edit(content = '❌ This minecraft account doesn\'t exist or never joined Hypixel.')
			try:
				userinfo['player']['socialMedia']
				userinfo['player']['socialMedia']['links']
				userinfo['player']['socialMedia']['links']['DISCORD']
			except:
				await chm.edit(content = '❌ This minecraft account doesn\'t have any Discord account linked yet.')
				await message.author.send('** How to link Discord and Hypixel?**\n1) Go to a Hypixel lobby.\n2) Right click "My Profile" in the hotbar, it is slot number 2.\n3) Click "Social Media". It is to the right of the Redstone block ("Status") button.\n4) Click "Discord". It is the second last option.\n5) Paste your Discord username into chat and hit enter. For reference your username is: lmnyx#0734\n6) You\'re done! Now wait at least 1 minute and verify again.')
				return
			curname = message.author.name+"#"+str(message.author.discriminator)
			if(curname != userinfo['player']['socialMedia']['links']['DISCORD']):
				await chm.edit(content = '❌ This minecraft account linked to other Discord account.')
			checkif = u.execute("SELECT * FROM users WHERE discordId = {0}".format(str(message.author.id)))
			d = u.fetchall()
			if(len(d) > 0):
				await chm.edit(content = '❌ You already have linked minecraft account!')
			else:
				await chm.edit(content = '✅ Linked!\n```This bot remembers Minecraft account for all servers. So if on other server you see this bot you don\'t really need to verify!```')
				u.execute("INSERT INTO users VALUES (?, ?)", (str(message.author.id), args[0]))
				users.commit()
			return

client.run(DISCORD_TOKEN)