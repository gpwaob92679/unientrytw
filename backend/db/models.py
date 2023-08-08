from django.core.validators import RegexValidator
from django.db import models

VALIDATE_ID = RegexValidator(r'^\d+$', 'ID contains non-digit characters.')


class School(models.Model):
    id = models.CharField(max_length=3,
                          primary_key=True,
                          validators=[VALIDATE_ID])
    name = models.TextField()

    def __str__(self):
        return f'School(id={self.id}, name={self.name})'


class Department(models.Model):
    id = models.CharField(max_length=6,
                          primary_key=True,
                          validators=[VALIDATE_ID])
    name = models.TextField()
    school = models.ForeignKey(School, models.CASCADE)

    def __str__(self):
        return f'Department(id={self.id}, name={self.name}, school={self.school})'


class ExamDivision(models.Model):
    id = models.CharField(max_length=4,
                          primary_key=True,
                          validators=[VALIDATE_ID])
    name = models.TextField()

    def __str__(self):
        return f'ExamDivision(id={self.id}, name={self.name})'


class ExamRoom(models.Model):
    id = models.CharField(max_length=6,
                          primary_key=True,
                          validators=[VALIDATE_ID])
    division = models.ForeignKey(ExamDivision, models.CASCADE)

    def __str__(self):
        return f'ExamRoom(id={self.id}, division={self.division})'
