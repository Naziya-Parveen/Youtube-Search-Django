import requests

from isodate import parse_duration

from django.conf import settings
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage
from .models import Videos, Query

def index(request):
	videos = []
	if request.method == 'GET':
		search_url = 'https://www.googleapis.com/youtube/v3/search'
		video_url = 'https://www.googleapis.com/youtube/v3/videos'

		search_query = request.GET.get('search'),
		try:
			isPresent = Query.objects.get(search=search_query)
		except ObjectDoesNotExist:
			isPresent = None

		print("isPresent : ",isPresent)
		#parameters passed for searching a video having query cricket
		if isPresent == None :
			query = Query()
			query.search = search_query
			query.save()

			search_params ={
				'part' : 'snippet',
				'q' : request.GET.get('search'),
				'maxResults' : 9,
				'type' :'video',
				'order' : 'date',
				'key' : settings.YOUTUBE_DATA_API_KEY,
			}
			#appending params in search url
			r = requests.get(search_url, params=search_params)
			#print(r.json())
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
				Videos_db = Videos()
				Videos_db.title = video_data['title']
				Videos_db.vid = video_data['id']
				Videos_db.url = video_data['url']
				Videos_db.duration = video_data['duration']
				Videos_db.thumbnail = video_data['thumbnail']
				Videos_db.query = query
				Videos_db.save()

		else:
			search_queryset = Query.objects.filter(search=search_query)
			search_query_id = search_queryset[0].id
			#print(search_queryset)
			all= Videos.objects.filter(query = search_query_id)
			
			videos = [entry for entry in all]
			print(videos)

	#pagination
	paginator = Paginator(videos,3)
	page_number = request.GET.get('page')
	print(request.GET.get('page'))
	try:
		page_obj = paginator.get_page(page_number)
	except EmptyPage:
		page_obj = paginator.get_page(1)

	get_copy = request.GET.copy()
	parameters = get_copy.pop('page',True) and get_copy.urlencode()

	context = {
		'videos' : page_obj,
		'parameters' : parameters,
	}
	return render(request,'search/index.html',context)