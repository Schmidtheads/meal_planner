import sys
import os

parent_path = os.path.abspath("..") + "\\meal_planner"
sys.path.append(parent_path)
print(sys.path)
from cookbook.models import Author, Cookbook
from recipe.models import Diner, Recipe, RecipeRating, RecipeType
from meal.models import Meal


class TableFactory():

    def __init__(self):
        pass


    def createTable(self, table_name, rows):
        table_obj = None
        if table_name.lower() == 'cookbook':
            table_obj = CookbookTable(table_name, rows)
        elif table_name.lower() == 'author':
            table_obj = AuthorTable(table_name, rows)
        elif table_name.lower() == 'diner':
            table_obj = DinerTable(table_name, rows)
        elif table_name.lower() == 'recipe':
            table_obj = RecipeTable(table_name, rows)

        return table_obj


class Table():

    def __init__(self, name, rows, foreign_keys=[]):
        self._name = name
        self._rows = rows
        for fk in foreign_keys:
            self._add_related_column(fk['column'], fk['related_table'])
        self._is_loaded = False


    @property
    def name(self):
        return self._name


    @property
    def rows(self):
        return self._rows


    @property 
    def related_rows(self):
        return self._related_columns


    @property
    def is_loaded(self):
        return self._is_loaded


    @property
    def pk_mapping(self):
        pk_mapping = None
        if self.is_loaded:
            pk_mapping = PrimaryKeyMapping(self.rows)
        return pk_mapping


    def load(self):
        # Iterate rows
        for r in self.rows:

            # Check if Cookbook already in table
            q = self._query_row_exists(r)

            self.get_related_objects()  #TODO: this may need to be changed

            if not q:
                t = self._create_table(r)
                t.save()

                # Get Django generated unique id
                django_id = t.id
                # Then add it to the data row being processed
                r['d_id'] = django_id
            else:
                t = None

        self._is_loaded = True


    def _query_row_exists(self, row):
        return None


    def _create_table(self, row):
        return None


    def _add_related_column(self, column_name, related_table):
        related_column = {
            'column': column_name, 
            'table': related_table, 
        }

        # check if related column already exists.
        # if it does replace it with new value
        found_match = False
        for rc in self._related_columns:
            if rc['column'].lower() == related_column['column'].lower():
                rc['table'] = related_column['table']
                found_match = True
                break
        
        if not found_match:
            self._related_columns.append(related_column)


    def get_related_objects(self):
        '''
        Replaces related columns id value with actual related object
        '''

        for rr in self.related_rows:
            #  get the d_id of the related table
            column = rr['column']
            related_table = rr['table']  # this is a Django table object

            # go through all the table rows and replace the related column with
            # an actual related object
            for r in self.rows:
                related_id = r[column]
                related_obj = related_table.objects.get(pk=related_id)
                r[column] = related_obj


class CookbookTable(Table):

    def __init__(self, name, rows, foreign_keys):
        super().__init__(name, rows, foreign_keys)


    # def load(self):
    #     # title, descr, author (fk), pdate, url=None, edition=None, image_path=None):

    #     # Iterate rows
    #     for r in self.rows:

    #         # Check if Cookbook already in table
    #         q = self._query_row_exists(r)

    #         self.get_related_objects()

    #         if not q:
    #             c = self._create_table(r)
    #             c.save()

    #             # Get Django generated unique id
    #             django_id = c.id
    #             # Then add it to the data row being processed
    #             r['d_id'] = django_id
    #         else:
    #             c = None

    #     self._is_loaded = True


    def _query_row_exists(self, row):
        query_value = row['title']
        q = Cookbook.objects.filter(title=query_value)
        return q


    def _create_table(self, row):
        table_object = Cookbook(
                    title=row['title'],
                    description=row['description'],
                    author=row['author'],
                    published_date=row['published_date'],
                    url=row['url'],
                    edition=row['edition'],
                    image=row['image']
                )
        return table_object


class AuthorTable(Table):

    def __init__(self, name, rows):
        super().__init__(name, rows)


    # def load(self):

    #     # Iterate rows of table
    #     for r in self.rows:

    #         # Check if Author already in table
    #         q = Author.objects.filter(first_name = r['first_name'], last_name = r['last_name'])

    #         if not q:
    #             a = Author(first_name = r['first_name'], last_name = r['last_name'])
    #             a.save()

    #             # Get Django generated unique id
    #             django_id = a.id
    #             # Then add it to the data row being processed
    #             r['d_id'] = django_id
    #         else:
    #             a = None

    #     return a

    def _query_row_exists(self, row):
        q = Author.objects.filter(first_name = row['first_name'], last_name = row['last_name'])
        return q


    def _create_table(self, row):
        t = Author(first_name = row['first_name'], last_name = row['last_name'])
        return t


class DinerTable(Table):

    def __init__(self, name, rows):
        super().__init__(name, rows)

    def load(self):

        # Iterate rows of table
        for r in self.rows:

            # Check if Author already in table
            q = Diner.objects.filter(
                first_name=r['first_name'], last_name=r['last_name'])

            if not q:
                a = Author(first_name=r['first_name'],
                           last_name=r['last_name'])
                a.save()

                # Get Django generated unique id
                django_id = a.id
                # Then add it to the data row being processed
                r['d_id'] = django_id
            else:
                a = None

        return a


class RecipeTable(Table):

    def __init__(self, name, rows, foreign_keys):
        super().__init__(name, rows, foreign_keys)


    def load(self):
        # name, cook_book (fk), page_number, notes):

        # Iterate rows
        for r in self.rows:

            # Check if Recipe already in table
            q = Recipe.objects.filter(title=r['name'])

            self.get_related_objects()

            if not q:
                c = Recipe(
                    name=r['name'],
                    cook_book=r['cookbook'],
                    page_number=r['page_number'],
                    notes=r['notes']
                )
                c.save()

                # Get Django generated unique id
                django_id = c.id
                # Then add it to the data row being processed
                r['d_id'] = django_id
            else:
                c = None


class RecipeRatingTable(Table):

    def __init__(self, name, rows, foreign_keys):
        super().__init__(name, rows, foreign_keys)


    def load(self):
        # rating, recipe (fk), diner (fk):

        # Iterate rows
        for r in self.rows:

            # Check if RecipeRating already in table
            # Get Diner and Recipe Object
            diner_obj = 1 #TODO: get actual diner
            recipe_obj = 1 #TODO: get actual recipe
            q = RecipeRating.objects.filter(recipe = recipe_obj).filter(diner = diner_obj)

            self.get_related_objects()

            if not q:
                c = Recipe(
                    name=r['name'],
                    cook_book=r['cookbook'],
                    page_number=r['page_number'],
                    notes=r['notes']
                )
                c.save()

                # Get Django generated unique id
                django_id = c.id
                # Then add it to the data row being processed
                r['d_id'] = django_id
            else:
                c = None        
    
class MealDatabase():
    '''
    Class that knows the Meal Planner data model and relationships between tables
    '''

    _TABLE_AUTHOR = 'Author'
    _TABLE_COOKBOOK = 'Cookbook'
    _TABLE_DINER = 'Diner'
    _TABLE_RECIPE = 'Recipe'
    _TABLE_RECIPETYPE = 'RecipeType'
    _TABLE_RECIPERATING = 'RecipeRating'
    _TABLE_MEAL = 'Meal'

    _DJANGO_ID_COL = 'd_id'

    _TABLES = [
        {
            'name': _TABLE_AUTHOR,
            'foreign_keys' : []
        },
        {
            'name': _TABLE_COOKBOOK,
            'foreign_keys': [
                {
                    'column': 'author',
                    'related_table': _TABLE_AUTHOR
                }
            ]
        },
        {
            'name': _TABLE_RECIPE,
            'foreign_keys': [
                {
                    'column': 'cook_book',
                    'related_table': _TABLE_COOKBOOK
                }
            ]
        },
        {
            'name': _TABLE_DINER,
            'foreign_keys': []
        },
        {
            'name': _TABLE
        }
    ]

    def __init__(self, database_connection):
        self._db_conn = database_connection

    
    @property
    def database_connection(self):
        return self._db_conn


    def load(self):
        '''
        Loads the database
        '''

        # Iterate through tables
        #   process tables so that tables with foreign key
        #   dependencies are loaded after tables they depend on

        # Iterate sorted table list
        #   Retrieve table data from source db
        #   Initialize table object with source data
        #   Check if table has foreign key dependencies
        #     if it does, send updated foreign key values (mapping)
        #   Load the table into django database


class PrimaryKeyMapping():

    def __init__(self, table_name, rows):
        self._table_name = table_name
        self._rows = []
        for r in rows:
            mapping = {
                'source_pk': r['id'],
                'dango_pk': r['d_id']    
            }
            self._rows.append(mapping)

    @property
    def rows(self):
        return self._rows

    
    def find_django_id(self, search_id):
        for r in self.rows:
            if r['source_fk'] == search_id:
                return r['d_id']
        return None
