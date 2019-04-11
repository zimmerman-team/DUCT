# Generated by Django 2.1.3 on 2019-04-09 17:33

from django.db import migrations, models
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('metadata', '0003_delete_other_added_other_responden_and_other_cleaning_technique'),
    ]

    operations = [
        migrations.AlterField(
            model_name='surveydata',
            name='ask_sensitive',
            field=models.CharField(choices=[('0', 'No'), ('1', 'Yes'), ('2', "Don't know")], help_text='It was possible for respondents to not answer certain questions if they found them to personal/sensitive?', max_length=100),
        ),
        migrations.AlterField(
            model_name='surveydata',
            name='considered_senstive',
            field=models.CharField(choices=[('0', 'No'), ('1', 'Yes'), ('2', "Don't know")], help_text='The data contains information which can be considered senstive? (f.e. financial, health, food security information)', max_length=100),
        ),
        migrations.AlterField(
            model_name='surveydata',
            name='data_cleaning_techniques',
            field=multiselectfield.db.fields.MultiSelectField(choices=[('0', 'Other'), ('1', 'Check for outliers'), ('2', 'Delete rows/columns with missing data'), ('3', 'Check of geodata'), ('4', 'Check consistency datatype per column'), ('5', 'Join, delimite or concatenate data')], help_text='Which data cleaning techniques did you use?', max_length=11),
        ),
        migrations.AlterField(
            model_name='surveydata',
            name='edit_sheet',
            field=models.CharField(choices=[('0', 'No'), ('1', 'Yes'), ('2', "Don't know")], help_text='Did you clean/edit the data before uploading it?', max_length=100),
        ),
        migrations.AlterField(
            model_name='surveydata',
            name='have_you_tested_tool',
            field=models.CharField(choices=[('0', 'No'), ('1', 'Yes'), ('2', "Don't know")], help_text='Have you tested the tool in a pilot or with a test group before conducting it?', max_length=100),
        ),
        migrations.AlterField(
            model_name='surveydata',
            name='select_respondents',
            field=multiselectfield.db.fields.MultiSelectField(choices=[('0', 'Other'), ('1', 'Simple random samplimng'), ('2', 'Stratified sampling'), ('3', 'Cluster sampling'), ('4', 'Systematic sampling'), ('5', 'Multistage sampling')], help_text='How did you select respondents?', max_length=11),
        ),
        migrations.AlterField(
            model_name='surveydata',
            name='staff_trained',
            field=models.CharField(choices=[('0', 'No'), ('1', 'Yes'), ('2', "Don't know")], help_text='Staff was trained on how to ask the sensitive information to avoid influencing the respondent’s answer?', max_length=100),
        ),
        migrations.AlterField(
            model_name='surveydata',
            name='who_did_you_test_with',
            field=multiselectfield.db.fields.MultiSelectField(choices=[('1', 'Enumerators'), ('2', 'Colleagues'), ('3', 'Respondents'), ('4', 'Representative group of respondents')], help_text='With who did you test the tool?', max_length=7),
        ),
    ]