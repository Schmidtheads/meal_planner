from django.core.management.base import BaseCommand

import copy
import sqlite3
import sys
from .dataload import MealDatabase

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

        mdb = MealDatabase(conn)
        print('Loading...')
        mdb.load()

        print('Done!')   


    def create_connection(self, database_path):

       conn = sqlite3.connect(database_path)

       return conn


 


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






