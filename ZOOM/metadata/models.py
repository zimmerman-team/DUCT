import os
from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import JSONField, ArrayField
from geodata.models import Geolocation
from mapping.models import Mapping
from multiselectfield import MultiSelectField


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
    ('Yes', 'Yes'),
    ('No', 'No'),
    ('Don\'t know', 'Don\'t know'),
)

WHO_TESTED_CHOICES = (
    ('Enumerators', 'Enumerators'),
    ('Colleagues', 'Colleagues'),
    ('Respondents', 'Respondents'),
    ('Representative group of respondents', 'Representative group of respondents'),
)

CONSINDERED_SENSITIVE_CHOICES = (
    ('Yes', 'Yes'),
    ('No', 'No'),
    ('Don\'t know', 'Don\'t know'),
)

HOW_SELECT_RESPONDENTS_CHOICES = (
    ('Simple random sampling', 'Simple random samplimng'),
    ('Stratified sampling', 'Stratified sampling'),
    ('Cluster sampling', 'Cluster sampling'),
    ('Systematic sampling', 'Systematic sampling'),
    ('Multistage sampling', 'Multistage sampling'),
    ('Other', 'Other'),
)

CLEANING_TECHNIQUES_CHOICES = (
    ('Check for outliers', 'Check for outliers'),
    ('Delete rows/columns with missing data', 'Delete rows/columns with missing data'),
    ('Check of geodata', 'Check of geodata'),
    ('Check consistency datatype per column', 'Check consistency datatype per column'),
    ('Join, delimite or concatenate data', 'Join, delimite or concatenate data'),
    ('Other', 'Other'),
)

class SurveyData(models.Model):
    have_you_tested_tool = models.CharField(
        max_length=100,
        help_text='Have you tested the tool in a pilot or with a test group before conducting it?',
        choices=HAVE_TESTED_CHOICES
    )
    who_did_you_test_with = MultiSelectField(choices=WHO_TESTED_CHOICES, help_text='With who did you test the tool?')
    considered_senstive = models.CharField(
        max_length=100,
        help_text='The data contains information which can be considered senstive? (f.e. financial, health, food security information)',
        choices=CONSINDERED_SENSITIVE_CHOICES
    )
    staff_trained = models.CharField(
        max_length=100,
        help_text='Staff was trained on how to ask the senstive information to avoid influencing the respondent’s anwers?',
        choices=CONSINDERED_SENSITIVE_CHOICES
    )
    ask_sensitive = models.CharField(
        max_length=100,
        help_text='It was possible for respondents to not answer certain questions if they found them to personal/senstive?',
        choices=CONSINDERED_SENSITIVE_CHOICES
    )
    select_respondents = MultiSelectField(choices=HOW_SELECT_RESPONDENTS_CHOICES, help_text='How did you select respondents?')
    other = models.CharField(max_length=200, help_text='If other, explain')
    how_many_respondents = models.CharField(max_length=100, help_text='How many respondents were interviewed/participated?')
    edit_sheet = models.CharField(max_length=100, help_text='Did you clean/edit the data before uploading it?', choices=CONSINDERED_SENSITIVE_CHOICES)
    data_cleaning_techniques = MultiSelectField(choices=CLEANING_TECHNIQUES_CHOICES, help_text='Which data cleaning techniques did you use?')


class File(models.Model):
    ## Metadata related fileds ##
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
    comments = models.TextField()  # caveats
    accessibility = models.CharField(max_length=100, choices=(
        ('o', 'open'), ('p', 'private'), ('r', 'request')))
    data_quality = models.CharField(max_length=1000)
    number_of_rows = models.IntegerField(
        help_text='No. of rows within dataset')
    number_of_rows_saved = models.IntegerField(
        null=True, help_text='No. of rows from dataset saved within ZOOM')
    file_types = models.CharField(
        max_length=100, choices=(
            ('csv', 'csv'), ('json', 'json')))
    survey_data = models.ForeignKey(SurveyData, related_name='file',  null=True, on_delete=models.SET_NULL)
    tags = models.ManyToManyField(FileTags)
    data_uploaded = models.DateField(auto_now_add=True)
    last_updated = models.DateField(auto_now=True)

    location = models.ForeignKey(
        Geolocation,
        on_delete=models.SET_NULL,
        null=True)
    source = models.ForeignKey(FileSource, on_delete=models.CASCADE)

    ## Back-end operational fields ##
    original_file_location = models.CharField(max_length=300)
    mapping_used = models.ForeignKey(Mapping, null=True, on_delete=models.SET_NULL) # JSONField(null=True)  # the Mapping used for the file
    file_status = models.CharField(max_length=100, choices=(
        ('1', 'Uploaded'), ('2', 'Error Correction'), ('3', 'Mapping'),
        ('4', 'Saved')))
    datatypes_overview_file_location = models.CharField(
        max_length=500)  # location
    error_file_location = models.CharField(max_length=500)  # location
    file = models.FileField(upload_to=upload_to, max_length=500, null=True)
    file_heading_list = JSONField(null=True)

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


def check_files():
    print('TODO')
    '''Deletes files not saved in data model.'''

    '''file_objects = Metadata.objects.all()
    found_files = []
    found_tmpfiles = []

    for file_ob in file_objects:
        found_files.append(str(file_ob.file))

        if FileDtypes.objects.filter(file=file_ob).count() > 0:
            try:
                found_tmpfiles.append(str(FileDtypes.objects.get(file=file_ob).dtype_name))
            except Exception:#make more specfic
                print(file_ob.title, ', Error, can't find dtype_name')

            try:
                found_tmpfiles.append(str(FileDtypes.objects.get(file=file_ob).dtype_dict_name))
            except Exception:
                print(file_ob.title, ', Error, can't find dtype_dict_name')
        else:
            if(file_ob.status == 5):##shouldn't happen, means no mapping saved for mapped file
                os.remove(file_ob.file)
                file_ob.delete()

            ##check are they mapped


    found_files = set(found_files)
    found_tmpfiles = set(found_tmpfiles)
    datasets_path = str(os.path.join(os.path.dirname(settings.BASE_DIR), 'ZOOM/media/datasets'))
    tmp_path = str(os.path.join(os.path.dirname(settings.BASE_DIR), 'ZOOM/media/tmpfiles'))
    tmp_dir = (os.listdir(tmp_path))
    datasets_dir = (os.listdir(datasets_path))
    datasets_dir = set([str(datasets_path + '/' + s) for s in datasets_dir])
    tmp_dir = set([str(tmp_path + '/' + s) for s in tmp_dir])

    diff_files, diff_tmpfiles = datasets_dir.difference(found_files), tmp_dir.difference(found_tmpfiles)
    file_sets = [diff_files, diff_tmpfiles]

    print('size datasets', len(datasets_dir))
    print('size diff', len(diff_files))
    count = 0

    for i in range(len(file_sets)):
        if len(file_sets[i]) > 0:
            for j in file_sets[i]:
                os.remove(j)
                count = count + 1

    print('Removed files: ', count)'''


def remove_unmapped_files():
    print('TODO')
    '''Deletes files that have not been mapped.'''
    '''
    count = 0
    file_objects = File.objects.all()
    for file_ob in file_objects:
        if file_ob.status < 5:

            try:
                os.remove(str(file_ob.file))
            except Exception: #shuld,'t happen'
                print('No file, ', file_ob)

            if FileDtypes.objects.filter(file=file_ob).count() > 0:
                try:
                    os.remove(str(FileDtypes.objects.get(file=file_ob).dtype_name))
                except Exception:#make more specfic
                    print(file_ob.title, ', Error, can't find dtype_name')

                try:
                    os.remove(str(FileDtypes.objects.get(file=file_ob).dtype_dict_name))
                except Exception:
                    print(file_ob.title, ', Error, can't find dtype_dict_name')
                FileDtypes.objects.get(file=file_ob).delete()

            file_ob.delete()
            count += 1

    print('Removed: ', count)'''
