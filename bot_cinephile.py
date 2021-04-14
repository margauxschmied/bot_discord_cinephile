import requests
import discord
import matplotlib.pyplot as plt

client = discord.Client()


def makeCamembert(information, my_filename):
    print(information)
    labels = []
    sizes = []
    for i in range(0, len(information), 2):
        labels.append(str(i // 2 + 1))
        sizes.append(information[i].get("votes") + information[i + 1].get("votes"))

    print(labels)
    print(sizes)
    # explode = (0, 0.1, 0, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)  # , explode=explode, shadow=True
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    plt.savefig(my_filename)
    plt.show()

    with open(my_filename, "rb") as fh:
        f = discord.File(fh, filename=my_filename)

    return f


async def getInformation(message, url):
    r = requests.get(url).text
    print(r)

    error = r[r.index("\"errorMessage\":") + len("\"errorMessage\":"): r.index("}")]
    print("error:" + error)

    if error == "":
        print("dedans")
        s = r[r.index("[{") + 2: r.index("}]")]
        s = s.split("},{")
        dic = {}
        for i in range(len(s)):
            s[i] = s[i].split(",")
            for j in range(len(s[i])):
                s[i][j] = s[i][j].split("\":\"")

                dic[s[i][j][0].replace("\"", "")] = s[i][j][1].replace("\"", "")
            s[i] = dic
            dic = {}
        return s
    else:
        await message.channel.send("Pas d'information disponible")
        return None


async def chooseMovie(information, message):
    print(information)
    movie = None
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
            if m.content.isnumeric():
                movie = chooseMovie[int(m.content)]
                await message.channel.send(movie)

        # idMovie = int(input("quel film voulez-vous voir?\n" + chooseMovieString))
        # while idMovie > len(chooseMovie) or idMovie < 1:
        #     idMovie = int(input("quel film voulez-vous voir?\n" + chooseMovieString))
        # movie = chooseMovie[idMovie - 1]
    else:
        movie = information[0].get("title")
        await message.channel.send(movie)
    return movie


def searchID(information, movie):
    for i in range(len(information)):
        if information[i].get("title") == movie:
            id = information[i].get("id")
            break
    return id


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # film = input("donne un film: ")
    # url = "https://imdb-api.com/en/API/Search/k_cybyscn8/" + film
    # print(url)
    # information = getInformation(url)
    #
    # movieChoose = chooseMovie(information)
    # idMovieChoose = searchID(information, movieChoose)
    # urlStat="https://imdb-api.com/en/API/UserRatings/k_cybyscn8/"+idMovieChoose
    #
    # print(getInformation(urlStat))

    @client.event
    async def on_reaction_add(reaction, user):
        print(reaction.emoji)
        if reaction.emoji == "😂":
            print("cool")


    @client.event
    async def on_ready():
        print('We have logged in as {0.user}'.format(client))


    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        elif message.content.startswith('$'):
            film = message.content[1:]
            url = "https://imdb-api.com/en/API/Search/k_cybyscn8/" + film

            information = await getInformation(message, url)
            if information is not None:
                movieChoose = await chooseMovie(information, message)
                if movieChoose is not None:
                    idMovieChoose = searchID(information, movieChoose)
                    urlStat = "https://imdb-api.com/en/API/UserRatings/k_cybyscn8/" + idMovieChoose
                    print(urlStat)

                    stat = await getInformation(message, urlStat)
                    if stat is not None:
                        file = makeCamembert(stat, 'camembert.png')
                        await message.channel.send(file=file)  # getInformation(urlStat))


    client.run("ODMwMDc4ODM4MDAzNzI4NDA0.YHBdKQ.HD9p1ljdLWY41dFopDfIe11BpbU")
