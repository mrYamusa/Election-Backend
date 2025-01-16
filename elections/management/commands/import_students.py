# your_app/management/commands/import_students.py
import pandas as pd
from django.core.management.base import BaseCommand
from elections.models import Student  # Adjust the import based on your model

class Command(BaseCommand):
    help = 'Import students from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str)

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        df = pd.read_csv(file_path)

        for index, row in df.iterrows():
            # Use the correct column names from the CSV
            Student.objects.create(
                reg_no=row['REGNO'],  # Match the column name in the CSV
                web_mail=row['WEBMAIL']  # Match the column name in the CSV
            )
        self.stdout.write(self.style.SUCCESS('Successfully imported students'))