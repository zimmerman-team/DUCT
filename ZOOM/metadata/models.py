import os
from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from geodata.models import Geolocation

def upload_to(instance, filename='test'):
    return os.path.join(os.path.join(settings.MEDIA_ROOT, settings.DATASETS_URL), filename)

class FileSource(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    name = models.CharField(unique=True ,max_length=100, null=False, blank=True)

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
    comments = models.TextField() # caveats
    accessibility = models.CharField(max_length=100, choices = (('o','open'), ('p','private'), ('r','request')))
    data_quality = models.CharField(max_length=1000)
    number_of_rows = models.IntegerField(help_text='No. of rows within dataset')
    number_of_rows_saved = models.IntegerField(null=True, help_text='No. of rows from dataset saved within ZOOM')
    file_types = models.CharField(max_length=100, choices = (('csv','csv'), ('json', 'json')))
    data_uploaded = models.DateField(auto_now_add=True)
    last_updated = models.DateField(auto_now=True)

    location = models.ForeignKey(Geolocation, on_delete=models.SET_NULL, null=True)
    source = models.ForeignKey(FileSource, on_delete=models.CASCADE)

    ## Back-end operational fields ##
    original_file_location = models.CharField(max_length=300)
    mapping_used = JSONField(null=True) # thge Mapping used for the file
    file_status = models.CharField(max_length=100, choices=(('1','Uploaded'), ('2','Error Correction'), ('3','Mapping'), ('4','Saved')))
    datatypes_overview_file_location = models.CharField(max_length=500)#location
    error_file_location = models.CharField(max_length=500)  # location
    file = models.FileField(upload_to=upload_to)

    def filename(self):
        print('check')
        return os.path.basename(self.file.name)

    def update_filename(self, updated_name):
        self.file.name = updated_name
        self.save()

    def get_file_path(self):
        print('check56')
        return os.path.join(settings.MEDIA_ROOT, settings.DATASETS_URL, os.path.basename(self.file.name))


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