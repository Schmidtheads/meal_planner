from django.core.management.base import BaseCommand

import copy
import pyodbc
import sys
from .dataload import TableFactory

_tables = ['Author', 'Diner', 'Cookbook', 'Meal', 'Recipe', 'RecipeType']
_meal_plan = []


class Command(BaseCommand):
    help = 'Loads Django database from MS Access'

    def add_arguments(self, parser):
        parser.add_argument('access_db', type=str,
                            help='Path to Access database')

        return super().add_arguments(parser)


    def handle(self, *args, **kwargs):

        access_db = kwargs['access_db']
        conn = self.create_connection(access_db)

        # Load the source data
        for t in _tables:
            try:
                rows = self.query_table(conn, t)

                table = TableFactory().createTable(t, rows)
                _meal_plan.append(table)

                # Load into Django database
                table.load()
            except:
                print(f'***WARNING*** table {t} could not be loaded')


    def create_connection(self, db_path):

        #connect_str = f'Driver={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={db_path};'
        connect_str = r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=D:\Projects\Other\meal_plan\data\MealPlanner.accdb;'
        conn = pyodbc.connect(connect_str)

        return conn


    def query_table(self, db_conn, table_name):

        cursor = db_conn.cursor()
        cursor.execute(f'select * from {table_name}')
        records = cursor.fetchall()

        columns = [column[0] for column in cursor.description]
        result_set = []
        for record in records:
            row = {}
            for i, value in enumerate(record):
                row[columns[i].lower()] = value
            result_set.append(row)

        return result_set


'''
Read in source data

for each author
    load author, return obj
    add author obj to list

for each cookbook
    look up author pk
    load cookbook, return obj
    add cookbook obj to list

for each recipe
    look up cookbook pk
    load recipe, return obj
    add recipe object to list

for each recipe type
    look up recipe pk
    look up if recipe type already loaded
    load recipe type

for each diner
    load diner, return obj
    add diner obj to list

for each recipe rating
    look up recipe pk
    look up diner pk
    load recipe rating

for each meal
    look up cookbook
    look up recipe
    load meal
    
'''






