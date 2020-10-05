from django.db import models

class Query(models.Model):
	search = models.CharField(max_length = 50)
	#videos = models.ManyToManyField(Videos) 
	
class Videos(models.Model):
	vid = models.CharField(max_length = 50)
	url = models.CharField(max_length = 500)
	title = models.CharField(max_length = 60)
	duration = models.IntegerField()
	thumbnail = models.ImageField()
	query = models.ForeignKey(Query, on_delete=models.CASCADE, null=True, blank=True)




