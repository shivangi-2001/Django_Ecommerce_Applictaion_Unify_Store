from django.core.management.base import BaseCommand
from django.db import connection
from pathlib import Path
import os


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("populating the Database with collection and Products")
        current_dir = os.path.dirname(__file__)
        file_path = os.path.join(current_dir, "seed.sql")

        # Read the contents of the file
        with open(file_path, 'r') as file:
            sql_statements = file.read().split(';')

        # Execute each SQL statement
        with connection.cursor() as cursor:
            for statement in sql_statements:
                # Skip empty statements
                if statement.strip():
                    cursor.execute(statement)

        self.stdout.write(self.style.SUCCESS('Database populated successfully'))
