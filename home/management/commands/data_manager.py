from django.core.management.base import BaseCommand

import copy
import sqlite3
import sys
from .dataload import TableFactory

_tables = ['Author', 'Diner', 'Cookbook', 'Meal', 'Recipe', 'RecipeType']
_meal_plan = []


class Command(BaseCommand):
    help = 'Loads Django database from SQL Lite database'

    def add_arguments(self, parser):
        parser.add_argument('db_path', type=str,
                            help='Path to SQL Lite database')

        return super().add_arguments(parser)


    def handle(self, *args, **kwargs):

        db_path = kwargs['db_path']
        conn = self.create_connection(db_path)

        # Load the source data
        for t in _tables:
            try:
                rows = self.query_table(conn, t)

                table = TableFactory().createTable(t, rows)
                _meal_plan.append(table)

                # Load into Django database
                print(f'Loading table {table.name}...')
                table.load()
            except Exception as ex:
                print(f'***WARNING*** table {t} could not be loaded\n{ex}')


    def create_connection(self, database_path):

       conn = sqlite3.connect(database_path)

       return conn


    def query_table(self, db_conn, table_name):

        cursor = db_conn.cursor()
        cursor.execute(f'select * from {table_name}')
        records = cursor.fetchall()

        columns = [column[0] for column in cursor.description]
        result_set = []
        for record in records:
            row = {}

            # Build the row    
            for i, value in enumerate(record):
                row[columns[i].lower()] = value

            # Add row to result set   
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






