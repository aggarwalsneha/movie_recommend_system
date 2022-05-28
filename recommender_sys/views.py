from django.shortcuts import render
from django.template import loader  
from django.http import HttpResponse 
import json
import pickle

# Create your views here.

content_df = pickle.load(open('recommender_sys/content_movie_list.pkl', 'rb'))
con_similar = pickle.load(open('recommender_sys/content_similarity.pkl','rb'))
cast_df = pickle.load(open('recommender_sys/cast_movie_list.pkl', 'rb'))
cast_similar = pickle.load(open('recommender_sys/cast_similarity.pkl','rb'))
pop_df=pickle.load(open('recommender_sys/popular_df.pkl','rb'))

def home(request):
    suggestions = get_suggestions()
    template = loader.get_template('recommender_sys/home.html')
    context={'suggestions':suggestions}
    return HttpResponse(template.render(context))

# get suggestions for autocomplete
def get_suggestions():
    return list(content_df['title'].str.capitalize())

# recommend similar movies 
def similarity(request):
    movie = request.POST['name']
    popular = rcmd(movie)
    con=content_based(movie)
    cast=cast_based(movie)
    m_str=",".join(popular)
    content=",".join(con)
    cast=",".join(cast)
    data={'mstr':m_str,'content':content,'cast':cast}
    print(json.dumps(data))
    return HttpResponse(json.dumps(data))

# recommend popular movies to user
def rcmd(movie):
    q_movies = pop_df.sort_values('weighted_average', ascending=False)
    li=q_movies['title'][:10].tolist()
    return li

# helper function to convert string to list
def convert_to_list(my_list):
    my_list = my_list.split('","')
    my_list[0] = my_list[0].replace('["','')
    my_list[-1] = my_list[-1].replace('"]','')
    return my_list

# getting data from AJAX request
def recommend(request):
    title = request.POST['title']
    cast_ids = request.POST['cast_ids']
    cast_names = request.POST['cast_names']
    cast_chars = request.POST['cast_chars']
    cast_bdays = request.POST['cast_bdays']
    cast_bios = request.POST['cast_bios']
    cast_places = request.POST['cast_places']
    cast_profiles = request.POST['cast_profiles']
    imdb_id = request.POST['imdb_id']
    poster = request.POST['poster']
    genres = request.POST['genres']
    overview = request.POST['overview']
    vote_average = request.POST['rating']
    vote_count = request.POST['vote_count']
    release_date = request.POST['release_date']
    runtime = request.POST['runtime']
    status = request.POST['status']
    rec_movies = request.POST['rec_movies']
    rec_posters = request.POST['rec_posters']
    crec_movies = request.POST['crec_movies']
    crec_posters = request.POST['crec_posters']
    casrec_movies = request.POST['casrec_movies']
    casrec_posters = request.POST['casrec_posters']
    # call the convert_to_list function for every string that needs to be converted to list
    rec_movies = convert_to_list(rec_movies)
    rec_posters = convert_to_list(rec_posters)
    crec_movies = convert_to_list(crec_movies)
    crec_posters = convert_to_list(crec_posters)
    casrec_movies = convert_to_list(casrec_movies)
    casrec_posters = convert_to_list(casrec_posters)
    cast_names = convert_to_list(cast_names)
    cast_chars = convert_to_list(cast_chars)
    cast_profiles = convert_to_list(cast_profiles)
    cast_bdays = convert_to_list(cast_bdays)
    cast_bios = convert_to_list(cast_bios)
    cast_places = convert_to_list(cast_places)
    
    # convert string to list (eg. "[1,2,3]" to [1,2,3])
    cast_ids = cast_ids.split(',')
    cast_ids[0] = cast_ids[0].replace("[","")
    cast_ids[-1] = cast_ids[-1].replace("]","")
    # rendering the string to python string
    for i in range(len(cast_bios)):
        cast_bios[i] = cast_bios[i].replace(r'\n', '\n').replace(r'\"','\"')
    # combining multiple lists as a dictionary which can be passed to the html file so that it can be processed easily and the order of information will be preserved
    movie_cards = {rec_posters[i]: rec_movies[i] for i in range(len(rec_posters))}
    cmovie_cards = {crec_posters[i]: crec_movies[i] for i in range(len(crec_posters))}
    casmovie_cards = {casrec_posters[i]: casrec_movies[i] for i in range(len(casrec_posters))}
    
    casts = {cast_names[i]:[cast_ids[i], cast_chars[i], cast_profiles[i]] for i in range(len(cast_profiles))}

    cast_details = {cast_names[i]:[cast_ids[i], cast_profiles[i], cast_bdays[i], cast_places[i], cast_bios[i]] for i in range(len(cast_places))}    

    # passing all the data to the html file
    template = loader.get_template('recommender_sys/recommend.html')
    context={'title':title,'poster':poster,'overview':overview,'vote_average':vote_average,'vote_count':vote_count,'release_date':release_date,'runtime':runtime,'status':status,'genres':genres,
        'movie_cards':movie_cards,'cmovie_cards':cmovie_cards,'casmovie_cards':casmovie_cards,'casts':casts,'cast_details':cast_details}
    return HttpResponse(template.render(context))

# recommendation based on similar genre
def content_based(movie):
    movie_index=content_df[content_df.title == movie].index[0]
    similarity_score=list(enumerate(con_similar[movie_index]))
    sorted_similar_movies=sorted(similarity_score,key=lambda x:x[1],reverse=True)
    recommended_movie_names = []
    for i in sorted_similar_movies[1:11]:
        recommended_movie_names.append(content_df.iloc[i[0]].title)
    return recommended_movie_names

# recommendation based on similar cast and crew
def cast_based(movie):
    movie_index=cast_df[cast_df.title == movie].index[0]
    similarity_score=list(enumerate(cast_similar[movie_index]))
    sorted_similar_movies=sorted(similarity_score,key=lambda x:x[1],reverse=True)
    movie_names = []
    cont_movie=content_based(movie)
    for i in sorted_similar_movies[1:]:
        if len(movie_names)<=10:
            if cast_df.iloc[i[0]].title not in cont_movie:
                movie_names.append(cast_df.iloc[i[0]].title)
        else:
            break
    return movie_names