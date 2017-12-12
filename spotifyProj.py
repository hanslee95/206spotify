import sys
import spotipy
import spotipy.util as util
import json
import sqlite3
import itertools
import collections
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
from plotly.graph_objs import *

################ GETTING THE API FOR SPOTIFY USING APP I MADE ########################################################################
username = 'hanslee_'
# reading songs that I have saved in my personal library.
scope = 'user-library-read'

# API Authorization using my spotify account
api = util.prompt_for_user_token(username,scope,client_id='c2fb9d8a11ae4eeeab9eb62415f6b09b',client_secret='5a909f1db45148d197dd8a950be3c8b8',redirect_uri='https://www.genrevisual.com')

# ############## CACHING THE DATA ###########################################################################################################################################################
CACHE_FNAME = "Saved_songs_cache.json"
try:
    cache_file = open(CACHE_FNAME, 'r') # Try to read the data from the file
    cache_contents = cache_file.read()  # If it's there, get it into a string
    CACHE_DICTION = json.loads(cache_contents) # And then load it into a dictionary
    cache_file.close() # Close the file, we're good, we got the data in a dictionary.
except:
    CACHE_DICTION = {}


#checking the cache of a particular user and returns that data or retrieves that cache'd data.
def get_saved_songs():
	# if statement is checking if you already looked it up, if you did, then use the thing you cache'd
	if 'items' in CACHE_DICTION:
		print('using cache')
		spotify_results = CACHE_DICTION['items']
	else:
		print('getting data from internet')
		spotify_results = spotipy.Spotify(auth=api)	
		CACHE_DICTION['items'] = spotify_results.current_user_saved_tracks(limit = 50)
		cache_file = open(CACHE_FNAME, 'w')
		#json.dumps prints out the string of dictionary in a json file in one line
		cache_file.write(json.dumps(CACHE_DICTION))
		cache_file.close()

	return CACHE_DICTION['items']

# ################ HELPER FUNCTIONS #####################################################################################################
# Takes an argument (mill) representing a number in milliseconds. Returns the converted minutes.
def millis_to_min(mill):
	x = mill / 1000
	seconds = x % 60
	x /= 60
	minutes = x % 60
	minutes = round(minutes, 2)
	number_dec = int(float(str(minutes-int(minutes))[1:]) * 60) / 100
	minutes = int(minutes)
	duration = minutes + number_dec
	
	return duration

def color_scl():
    lst_col_scale = []
    # creating the color scale with color corresponding to a number determined by the range of 0 to max of popularity
    count = 0
    while(count <= 100):
        lst_col_scale.append(count)
        count = count + 1   
    return lst_col_scale     

################## CREATING DATABASE AND LOADING IN DATA ###########################################################################################
#Have to organize data into list of tuples so it can be sorted by popularity/duration pairs and then correlate popularity with color. 

# list of tuples 
lst_tup = []

saved_songs = get_saved_songs()

conn = sqlite3.connect('songs.sqlite', timeout = 10)
cur = conn.cursor()
# creating users table
cur.execute('DROP TABLE IF EXISTS Songs')
cur.execute("CREATE TABLE SONGS (popularity NUMBER, duration NUMBER)")

for songs in saved_songs['items']:
    item = songs['track']
    # calling converter function here (ms -> minutes)
    duration = millis_to_min(item['duration_ms'])
    tupl = item['popularity'], duration
    cur.execute('INSERT INTO Songs (popularity, duration) VALUES (?, ?)',tupl)    

#Use the database connection to commit the changes to the database    
conn.commit()    

cur.execute('SELECT popularity FROM Songs')
lst_tupx = cur.fetchall()
lst_px = [elem[0] for elem in lst_tupx]

cur.execute('SELECT duration FROM Songs')
lst_tupy = cur.fetchall()
lst_dy = [elem[0] for elem in lst_tupy]

lst_tup = list(zip(lst_px, lst_dy))

# sorted the list of tuples by popularity
lst_tup.sort(key=lambda x: x[0])
lst_x = [i[0] for i in lst_tup]
lst_y = [i[1] for i in lst_tup] 

################## USING PLOTLY PYTHON TO VISUALIZE DATA #####################################################################################
lst_col_scl = color_scl()
# Creates scatter plot with x and y axis being labeled popularity/duration respectively.
trace = go.Scatter(
    x = lst_x,
    y = lst_y,
    marker = Marker(
    	size = 16,
    	cmax = max(lst_x),
    	cmin = 0,
    	color=lst_col_scl,
    	colorbar=ColorBar(
            title='Popularity'
        ),
        colorscale='Viridis'
    ),
    mode = 'markers'
)
# styling and labeling title/x-axis/y-axis
layout = go.Layout(
    title='POPULAR MUSIC TASTE?',
    xaxis=dict(
        title='Popularity (Number of Streams)',
        titlefont=dict(
            family='Courier New, monospace',
            size=18,
            color='#7f7f7f'
        )
    ),
    yaxis=dict(
        title='Duration of Song (min)',
        titlefont=dict(
            family='Courier New, monospace',
            size=18,
            color='#7f7f7f'
        )
    )
)
data = [trace]
fig = go.Figure(data=data, layout=layout)
# displays on my plotly account under "scatter-spotify"
py.iplot(fig, filename='scatter-spotify')

		
