from django.db import models


class School(models.Model):
    id = models.CharField(max_length=3, primary_key=True)
    name = models.TextField()

    def __str__(self):
        return f'School(id={self.id}, name={self.name})'
