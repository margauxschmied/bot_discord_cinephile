import asyncio
import random

import requests
import discord
import matplotlib.pyplot as plt
from discord.ext.commands import bot

import os
from dotenv import load_dotenv

from DB import data

client = discord.Client()
botColor = discord.Colour(0xfefc2e)

load_dotenv()

IMDbKey=os.getenv('IMDbKey')
token_bot=os.getenv('token_bot')
MDP_BDD=os.getenv('MDP_BDD')


def makeCamembert(information, my_filename):  # make a circle graph of rating
    labels = []
    sizes = []
    for i in range(0, len(information), 2):
        labels.append(str(i // 2 + 1))
        sizes.append(information[i].get("votes") + information[i + 1].get("votes"))

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')

    plt.savefig(my_filename, transparent=True)
    plt.show()

    with open(my_filename, "rb") as fh:
        f = discord.File(fh, filename=my_filename)

    return f


async def getInformation(message, url):  # extract information about a request
    r = requests.get(url).text

    error = r[r.index("\"errorMessage\":\"") + len("\"errorMessage\":\""): r.index("\"}")]

    if error == "":
        s = r
        if "[{" in s and "}]" in s:
            s = r[r.index("[{") + 2: r.index("}]")]

        s = s.split("},{")

        dic = {}
        for i in range(len(s)):
            s[i] = s[i].split("\",\"")
            for j in range(len(s[i])):
                s[i][j] = s[i][j].split("\":\"")
                dic[s[i][j][0].replace("\"", "")] = s[i][j][1].replace("\"", "")
            s[i] = dic
            dic = {}
        return s
    else:
        await message.channel.send("Pas d'information disponible")
        return None


async def chooseMovie(information, message):  # in the case where several movies have the same name
    movie = None  # this function made choose to the user the right movie
    if len(information) > 1:
        chooseMovie = []
        chooseMovieString = ""
        for i in range(len(information)):
            title = information[i].get('title')
            chooseMovie.append(title)
            chooseMovieString += (str(chooseMovie.index(title)) + ". " + title + "\n")

        if len(chooseMovie) > 10:
            await message.channel.send("Trop de resultat")

        else:
            await message.channel.send("Quel film voulez-vous voir?\n" + chooseMovieString)
            m = await client.wait_for('message')
            if m.content.isnumeric() and 0 <= int(m.content) < len(information):
                movie = information[int(m.content)]
    else:
        movie = information[0]
    return movie


def printTitles(info, information, message):  # return a string with numbered title
    titles = ""
    for i in range(len(information)):
        title = information[i].get('title')
        titles += (str(info.index(information[i]) + 1) + ". " + title + "\n")
    return titles


def searchID(information, movie):  # search the good id of a movie
    id = None
    for i in range(len(information)):
        if information[i].get("title") == movie:
            id = information[i].get("id")
            break
    return id


async def pretraitement(message, commande, urlInfo):
    film = message.content[len(commande):]
    url = "https://imdb-api.com/en/API/Search/"+IMDbKey+"/" + film

    movieChoose = None
    info = None
    information = await getInformation(message, url)
    if information is not None:
        movieInfo = await chooseMovie(information, message)
        if movieInfo is not None:
            movieChoose = movieInfo.get('title')
            idImdb = movieInfo.get('id')
            urlInfo = urlInfo + str(idImdb)

            info = await getInformation(message, urlInfo)

    return movieChoose, info


async def randomMovie(message):  # give a random movie in most popular movies
    information = await getInformation(message, "https://imdb-api.com/en/API/MostPopularMovies/"+IMDbKey)
    id = random.randint(0, len(information))
    return information[id]


async def randomTV(message): # give a random series in most popular series
    information = await getInformation(message, "https://imdb-api.com/en/API/MostPopularTVs/"+IMDbKey)
    id = random.randint(0, len(information))
    return information[id]


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message): #when we receved a message
    top50 = False
    author = message.author.id
    print(author)

    if message.content.startswith('$rating '):
        movieChoose, stat = await pretraitement(message, '$rating ',
                                                "https://imdb-api.com/en/API/UserRatings/"+IMDbKey+"/")
        if stat is not None:
            file = makeCamembert(stat, 'camembert.png')
            embed = discord.Embed(title=movieChoose, colour=botColor)
            embed.set_image(url="attachment://camembert.png")

            await message.channel.send(embed=embed, file=file)  # getInformation(urlStat))

    elif message.content.startswith('$trailer '):
        movieChoose, trailerInfo = await pretraitement(message, '$trailer ',
                                                       "https://imdb-api.com/en/API/YouTubeTrailer/"+IMDbKey+"/")
        if trailerInfo is not None:
            await message.channel.send(trailerInfo[0].get('videoUrl'))  # embed=embed)

    elif message.content.startswith('$top50Movies'):
        information = await getInformation(message, "https://imdb-api.com/en/API/Top250Movies/"+IMDbKey)
        if information is not None:
            embed = discord.Embed(title="Top 50 movies", color=botColor)
            top50 = True

    elif message.content.startswith('$top50TVs'):
        information = await getInformation(message, "https://imdb-api.com/en/API/Top250TVs/"+IMDbKey)
        if information is not None:
            embed = discord.Embed(title="Top 50 TVs", color=botColor)
            top50 = True

    elif message.content.startswith('$mostPopularMovies'):
        information = await getInformation(message, "https://imdb-api.com/en/API/MostPopularMovies/"+IMDbKey)
        if information is not None:
            embed = discord.Embed(title="50 most popular movies", color=botColor)
            top50 = True

    elif message.content.startswith('$mostPopularTVs'):
        information = await getInformation(message, "https://imdb-api.com/en/API/MostPopularTVs/"+IMDbKey)
        if information is not None:
            embed = discord.Embed(title="50 most popular TVs", color=botColor)
            top50 = True

    elif message.content.startswith('$randomMovie'):
        information = None
        while information is None:
            movie = await randomMovie(message)
            information = await getInformation(message,
                                               "https://imdb-api.com/en/API/YouTubeTrailer/"+IMDbKey+"/" + movie.get(
                                                   "id"))
            if information is not None:
                await message.channel.send(information[0].get('videoUrl'))

    elif message.content.startswith('$randomTV'):
        information = None
        while information is None:
            TV = await randomTV(message)
            information = await getInformation(message,
                                               "https://imdb-api.com/en/API/YouTubeTrailer/"+IMDbKey+"/" + TV.get("id"))
            if information is not None:
                await message.channel.send(information[0].get('videoUrl'))

    elif message.content.startswith('$movieBattle'):
        time = message.content[len('$chooseMovie'):]
        time = time.replace(" ", "")

        if time == "":
            time = 30
        else:
            time = int(time)

        titles = []

        for i in range(5):
            titles.append(await randomMovie(message))

        REACTIONS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]

        embed = discord.Embed(title="You have 5s to choose a movie:", description=printTitles(titles, titles, message),
                              color=botColor)
        message = await message.channel.send(embed=embed)
        for reaction in REACTIONS:
            await message.add_reaction(reaction)
        for i in range(1, time):
            await asyncio.sleep(1)
            embed = discord.Embed(title="You have " + str(time - i) + "s to choose a movie:",
                                  description=printTitles(titles, titles, message),
                                  color=botColor)
            await message.edit(embed=embed)

        message = await message.channel.fetch_message(message.id)
        nbMax = message.reactions[0].count
        idMax = 0
        id = 0

        for reaction in message.reactions:
            if reaction.count > nbMax:
                nbMax = reaction.count
                idMax = id
            id += 1

        embed = discord.Embed(title="And the winner is...", color=botColor)
        await message.channel.send(embed=embed)
        await asyncio.sleep(1)
        embed = discord.Embed(title=titles[idMax].get("title"), color=botColor)
        await message.channel.send(embed=embed)

    elif message.content.startswith('$help'):
        title = "CineBot commands!"

        embed = discord.Embed(title=title, color=botColor)

        embed.add_field(name="$rating MOVIE", value="Displays rating of MOVIE",
                        inline=False)
        embed.add_field(name="$trailer MOVIE", value="Displays the trailer of MOVIE",
                        inline=False)
        embed.add_field(name="$top50Movies", value="Displays the top 50 movies",
                        inline=False)
        embed.add_field(name="$top50TVs", value="Displays the top 50 series",
                        inline=False)
        embed.add_field(name="$mostPopularMovies", value="Displays the 50 most popular movies",
                        inline=False)
        embed.add_field(name="$mostPopularTVs", value="Displays the 50 most popular series",
                        inline=False)
        embed.add_field(name="$randomMovie", value="Displays the trailer of a random movie",
                        inline=False)
        embed.add_field(name="$randomTV", value="Displays the trailer of a random serie",
                        inline=False)
        embed.add_field(name="$movieBattle ?TIME", value="Displays 5 random movie and if TIME exist at the end of the "
                                                         "timer the movie with the most reaction win else it's after 30s",
                        inline=False)
        await message.channel.send(embed=embed)

    if top50:
        await message.channel.send(embed=embed)
        for i in range(0, 50, 10):
            embed = discord.Embed(description=printTitles(information, information[i:i + 10], message), color=botColor)
            await message.channel.send(embed=embed)

if __name__ == '__main__':
    # connection = data.create_db_connection("localhost", "root", MDP_BDD, "cineBot")
    client.run(token_bot)
