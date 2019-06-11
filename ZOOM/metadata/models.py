import os

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from multiselectfield import MultiSelectField

from geodata.models import Geolocation


def upload_to(instance, filename='test'):
    return os.path.join(
        os.path.join(
            settings.MEDIA_ROOT,
            settings.DATASETS_URL),
        filename)


class FileTags(models.Model):
    name = models.CharField(
        unique=True,
        max_length=100,
        null=False)


class FileSource(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    name = models.CharField(
        unique=True,
        max_length=100,
        null=False)

    def __str__(self):
        return str(self.id)


HAVE_TESTED_CHOICES = (
    ('0', 'No'),
    ('1', 'Yes'),
    ('2', 'Don\'t know')
)

WHO_TESTED_CHOICES = (
    ('1', 'Enumerators'),
    ('2', 'Colleagues'),
    ('3', 'Respondents'),
    ('4', 'Representative group of respondents')
)

CONSINDERED_SENSITIVE_CHOICES = (
    ('0', 'No'),
    ('1', 'Yes'),
    ('2', 'Don\'t know')
)

CLEANING_TECHNIQUES_CHOICES = (
    ('0', 'Other'),
    ('1', 'Check for outliers'),
    ('2', 'Delete rows/columns with missing data'),
    ('3', 'Check of geodata'),
    ('4', 'Check consistency datatype per column'),
    ('5', 'Join, delimite or concatenate data')
)


class SurveyData(models.Model):
    have_you_tested_tool = models.CharField(
        max_length=100,
        help_text='Have you tested the tool in a pilot or with '
                  'a test group before conducting it?',
        choices=HAVE_TESTED_CHOICES)
    who_did_you_test_with = MultiSelectField(
        choices=WHO_TESTED_CHOICES,
        help_text='With who did you test the tool?')
    considered_senstive = models.CharField(
        max_length=100,
        help_text='The data contains information which can be considered '
                  'senstive? (f.e. financial, health,'
                  ' food security information)',
        choices=CONSINDERED_SENSITIVE_CHOICES)
    staff_trained = models.CharField(
        max_length=100,
        help_text='Staff was trained on how to ask the sensitive '
                  'information to avoid influencing the respondent’s answer?',
        choices=CONSINDERED_SENSITIVE_CHOICES)
    ask_sensitive = models.CharField(
        max_length=100,
        help_text='It was possible for respondents to not answer certain '
                  'questions if they found them to personal/sensitive?',
        choices=CONSINDERED_SENSITIVE_CHOICES)
    select_respondents = models.CharField(
        max_length=200, help_text='How did you select respondents?',
        null=True, blank=True, default='')
    how_many_respondents = models.CharField(
        max_length=100,
        help_text='How many respondents were interviewed/participated?')
    edit_sheet = models.CharField(
        max_length=100,
        help_text='Did you clean/edit the data before uploading it?',
        choices=CONSINDERED_SENSITIVE_CHOICES)
    data_cleaning_techniques = MultiSelectField(
        choices=CLEANING_TECHNIQUES_CHOICES,
        help_text='Which data cleaning techniques did you use?')
    other_cleaning_technique = models.CharField(
        max_length=200, help_text='If other respondent, explain',
        null=True, blank=True, default='')

    def __str__(self):
        return str(self.id)


class File(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    title = models.CharField(max_length=100,)
    description = models.TextField()
    contains_subnational_data = models.BooleanField()
    organisation = models.CharField(max_length=100)
    maintainer = models.CharField(max_length=100)
    date_of_dataset = models.DateField()
    methodology = models.CharField(max_length=150)
    define_methodology = models.TextField()
    update_frequency = models.CharField(max_length=100)
    comments = models.TextField()
    accessibility = models.CharField(max_length=100, choices=(
        ('o', 'open'), ('p', 'private'), ('r', 'request'), ('a', 'all')))
    data_quality = models.CharField(max_length=1000)
    number_of_rows = models.IntegerField(
        help_text='No. of rows within dataset')
    number_of_rows_saved = models.IntegerField(
        null=True, help_text='No. of rows from dataset saved within ZOOM')
    file_types = models.CharField(
        max_length=100, choices=(
            ('csv', 'csv'), ('json', 'json')))
    survey_data = models.ForeignKey(
        SurveyData,
        related_name='file',
        null=True,
        on_delete=models.SET_NULL)
    tags = models.ManyToManyField(FileTags)
    data_uploaded = models.DateField(auto_now_add=True)
    last_updated = models.DateField(auto_now=True)

    location = models.ForeignKey(
        Geolocation,
        on_delete=models.SET_NULL,
        null=True)
    source = models.ForeignKey(FileSource, on_delete=models.CASCADE)
    original_file_location = models.CharField(max_length=300)
    file_status = models.CharField(max_length=100, choices=(
        ('1', 'Uploaded'), ('2', 'Error Correction'), ('3', 'Mapping'),
        ('4', 'Saved')))
    datatypes_overview_file_location = models.CharField(
        max_length=500)
    error_file_location = models.CharField(max_length=500)
    file = models.FileField(upload_to=upload_to, max_length=500, null=True)
    file_heading_list = JSONField(null=True)

    def __str__(self):
        return str(self.id)

    def filename(self):
        return os.path.basename(self.file.name)

    def update_filename(self, updated_name):
        self.file.name = updated_name
        self.save()

    def get_file_path(self):
        return os.path.join(
            settings.MEDIA_ROOT,
            settings.DATASETS_URL,
            os.path.basename(
                self.file.name))
