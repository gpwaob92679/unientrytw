from django.db import models


class School(models.Model):
    id = models.CharField(max_length=3, primary_key=True)
    name = models.TextField()

    def __str__(self):
        return f'School(id={self.id}, name={self.name})'


class Department(models.Model):
    id = models.CharField(max_length=6, primary_key=True)
    name = models.TextField()
    school = models.ForeignKey(School, models.CASCADE)

    def __str__(self):
        return f'Department(id={self.id}, name={self.name}, school={self.school})'
