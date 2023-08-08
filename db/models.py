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


class Examinee(models.Model):
    id = models.CharField(max_length=8,
                          primary_key=True,
                          validators=[VALIDATE_ID])
    name = models.TextField(blank=True)
    exam_room = models.ForeignKey(ExamRoom, models.CASCADE)
    accepted_departments = models.ManyToManyField(Department,
                                                  'accepted_examinees')
    final_accepted_department = models.ForeignKey(Department,
                                                  models.CASCADE,
                                                  'final_accepted_examinees',
                                                  null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exam_room = ExamRoom.objects.get(id=self.id[:6])

    def __str__(self):
        return f'Examinee(id={self.id}, name={self.name})'
