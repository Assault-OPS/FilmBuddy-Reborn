import discord 
from discord import app_commands 
from discord.ext import commands 
from pyrebase import pyrebase 
from Designer import Designer
import json
import requests
from io import BytesIO


# Setting up utility functions 

async def get_data(url,query):
    data = requests.Session().get(url=url+query)
    return data.json()
async def genre_generator(ids):
    with open("genre.json","r") as file:
        data = json.load(file)
    return (i.get("name") for i in data["genres"] if i.get("id") in ids.get("genre_ids"))

async def lang_gen(code):
    with open("lang.json","r",encoding="utf8") as lang:
        data = json.load(lang)
    if data.get(code) is not None: return data.get(code).get("name")


# Firebase credentials
firebaseConfig = {
#Classified information
  }

# Setting up Firebase
firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()


# Setting up basic keys
with open("credential.json",'r') as f:
    creds = json.load(f)
    p_path,apikey,ownerids,token,TOKEN = creds["poster_path"],creds["_apiKey"],creds["owners"],creds["token"],creds["BOT_TOKEN"]


# Setting up API URLs
movie_url = f"https://api.themoviedb.org/3/search/movie?api_key={apikey}&language=en-US&page=1&include_adult=false&query="
tv_url = f"https://api.themoviedb.org/3/search/tv?api_key={apikey}&language=en-US&page=1&include_adult=false&query="

# Setting up Elements
elements = ["title","release_date","overview","vote_average","poster_path","genre_ids","original_language","backdrop_path"]
elements2 = ["name","first_air_date","overview","vote_average","poster_path","genre_ids","original_language","backdrop_path"]


bot = commands.Bot(command_prefix="find ",intents=discord.Intents.default())

async def process(interaction,query,url,elem,page,guild_id):
    if guild_id is None:
        guild_id=interaction.guild_id
    if elem is None:
        elem = elements
    await interaction.response.defer()
    mov = await get_data(url,"%20".join(query.split()))
    mov = mov.get("results")
    if len(mov) != 0:
        if db.child("img").child(guild_id).get().val() is None:
            db.child("img").update({guild_id:2})
        datas = [db.child("img").child(guild_id).get().val()]
        for i in elem:
            if all((i=="poster_path",mov[page].get(i) != None)):
                datas.append(p_path+mov[page].get(i))
            elif all((i=="backdrop_path",mov[page].get(i) != None)):
                datas.append(p_path+mov[page].get(i))
            elif all((i=="genre_ids",mov[page].get(i) != None)):
                datas.append([*await genre_generator(mov[page])])
            elif all((i=="original_language",mov[page].get(i) != None)):
                datas.append(await lang_gen(mov[page].get(i)))
            else:
                datas.append(mov[page].get(i))
        movie_info = Designer(*datas)
        print(datas)
        image = await movie_info.design()
        with BytesIO() as binary:
            image.save(binary,'JPEG')
            binary.seek(0)
            await interaction.followup.send(file=discord.File(fp=binary,filename=datas[1].replace(' ','_')+'.jpg'))
            return
    await interaction.followup.send("No results Found.")



@bot.event 
async def on_ready():
    print("[LOG] Ready")
    try:
        synced = await bot.tree.sync()
        print("[LOG] commands synced")
    except Exception as e:
        print(f"[LOG] Couldn't perform sync due to following\n{e}")


@bot.event
async def on_guild_join(guild):
    db.child("img").update({guild.id:4})


@bot.tree.command(name="movie")
async def _movie(interaction:discord.Interaction,*,query:str,page:int=0):
    await process(interaction,query,movie_url,None,page,None)


@bot.tree.command(name="show")
async def _show(interaction:discord.Interaction,*,query:str,page:int=0):
    await process(interaction,query,tv_url,elements2,page,None)




if __name__ == "__main__":
    bot.run(TOKEN)

