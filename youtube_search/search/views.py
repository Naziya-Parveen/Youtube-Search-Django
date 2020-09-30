import requests

from isodate import parse_duration

from django.conf import settings
from django.shortcuts import render

def index(request):
	videos = []
	if request.method == 'POST':
		search_url = 'https://www.googleapis.com/youtube/v3/search'
		video_url = 'https://www.googleapis.com/youtube/v3/videos'

		#parameters passed for searching a video having query cricket
		search_params ={
			'part' : 'snippet',
			'q' : request.POST['search'],
			'maxResults' : 9,
			'type' :'video',
			'order' : 'date',
			'key' : settings.YOUTUBE_DATA_API_KEY,
		}
		#appending params in search url
		r = requests.get(search_url, params=search_params)
		results = r.json()['items']

		#storing all the video ids in a dictionary
		video_ids = []
		for result in results:
			video_ids.append(result['id']['videoId'])

		#parameters passed for getting more details of videos whose ids are stored in video_ids
		video_params = {
			'key' : settings.YOUTUBE_DATA_API_KEY,
			'part' : 'snippet,contentDetails',
			'maxResults' : 9,
			'id' : ','.join(video_ids),
		}
		#appending params in video url
		r = requests.get(video_url, params=video_params)
		results = r.json()['items']

		for result in results :
			video_data = {
				'title' : result['snippet']['title'],
				'id' : result['id'],
				'url' : f'https://www.youtube.com/watch?v={result["id"]}',
				'duration' : int(parse_duration(result['contentDetails']['duration']).total_seconds()//60),
				'thumbnail' : result['snippet']['thumbnails']['high']['url']
			}
			videos.append(video_data)

	context = {
		'videos' : videos
	}
	
	return render(request,'search/index.html',context)