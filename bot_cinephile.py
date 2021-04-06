import requests

def get_information(url):
    r = requests.get(url).text
    
    s = r[ r.index("[{")+2 : r.index("}]")]
    s=s.split("},{")
    dic={}
    for i in range(len(s)):
        s[i]=s[i].split(",")
        for j in range(len(s[i])):
            s[i][j]=s[i][j].split("\":\"")
            
            dic[s[i][j][0].replace("\"","")]=s[i][j][1].replace("\"","")
        s[i]=dic
        dic={}
    return s

def chooseMovie(information):
    if len(information) == 1:
        chooseMovie=[]
        chooseMovieString=""
        for i in range(len(information)):
            title=information[i].get("title")
            chooseMovie.append(title)
            chooseMovieString+=(str(chooseMovie.index(title)+1)+". "+title+"\n")
        idMovie=int(input ("quel film voulez-vous voir?\n"+ chooseMovieString))
        while idMovie>len(chooseMovie)or idMovie<1:
            idMovie=int(input ("quel film voulez-vous voir?\n"+ chooseMovieString))
        movie=chooseMovie[idMovie-1]
    else:
        movie=title=information[i].get("title")

    return movie
    
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    film= input("donne un film: ")
    url="https://imdb-api.com/en/API/Search/k_cybyscn8/" + film
    print(url)
    information=get_information(url)
    
    movieChoose=chooseMovie(information)



    print(movieChoose)