from django.db import models
from django.contrib.postgres.fields import JSONField


class Post(models.Model):
    title = models.CharField(max_length=512, null=True, blank=True)
    body = models.TextField(null=True, blank=True)
    posted_at = models.DateTimeField(null=False)
    data = JSONField()

    def __str__(self):
        return self.body


class Photo(models.Model):
    caption = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='photos')
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    
    def __str__(self):
        return self.caption
