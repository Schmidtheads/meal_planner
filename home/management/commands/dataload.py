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
        self._fk_mapping = []
        self._is_loaded = False


    @property
    def name(self):
        return self._name


    @property
    def rows(self):
        return self._rows


    @property 
    def related_columns(self):
        return self._related_columns


    @property
    def is_loaded(self):
        return self._is_loaded


    @property
    def pk_mapping(self):
        pk_mapping = None
        if self.is_loaded:
            pk_mapping = PrimaryKeyMapping(self, self.rows)
        return pk_mapping


    @property
    def django_table(self):
        # This method MUST be overridden in subclass
        return None


    def add_fk_mapping(self, fk_mapping):
        self._fk_mapping.append(fk_mapping)


    def get_fk_mapping(self, related_table, source_fk):
        for fkm in self._fk_mapping:
            if fkm.table_name.lower() == related_table.lower():
                return fkm.find_django_id(source_fk)
        return None


    def load(self):
        # Iterate rows
        for r in self.rows:

            # Check if Cookbook already in table
            q = self._query_row_exists(r)

            for rc in self.related_columns:
                r[rc['column']] = self.get_fk_mapping(rc['table'], r[rc['column']])

            if not q:
                t = self._create_row(r)
                t.save()

                # Get Django generated unique id
                django_id = t.id
                # Then add it to the data row being processed
                r['d_id'] = django_id
            else:
                # Assumption that only one record will be returned
                r['d_id'] = q[0].id

        self._is_loaded = True


    def _query_row_exists(self, row):
        return None


    def _create_row(self, row):
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


class CookbookTable(Table):

    def __init__(self, name, rows, foreign_keys):
        super().__init__(name, rows, foreign_keys)


    @property
    def django_table(self):
        return Cookbook


    def _query_row_exists(self, row):
        query_value = row['title']
        q = Cookbook.objects.filter(title=query_value)
        return q


    def _create_row(self, row):
        t = Cookbook(
            title=row['title'],
            description=row['description'],
            author=row['author'],
            published_date=row['published_date'],
            url=row['url'],
            edition=row['edition'],
            image=row['image']
        )
        return t


class AuthorTable(Table):

    def __init__(self, name, rows):
        super().__init__(name, rows)


    @property
    def django_table(self):
        return Author

        
    def _query_row_exists(self, row):
        q = Author.objects.filter(first_name = row['first_name'], last_name = row['last_name'])
        return q


    def _query_row_by_django_id(self, django_id):
        # only if table is loaded!
        if self.is_loaded:
            q = Author.objects.get(pk=django_id)
            return q
        return None


    def _create_row(self, row):
        t = Author(first_name = row['first_name'], last_name = row['last_name'])
        return t


class DinerTable(Table):

    def __init__(self, name, rows):
        super().__init__(name, rows)


    @property
    def django_table(self):
        return Diner


    def _query_row_exists(self, row):
        q = Diner.objects.filter(first_name=row['first_name'], last_name=row['last_name'])
        return q


    def _create_row(self, row):
        t = Diner(first_name = row['first_name'], last_name = row['last_name'])
        return t


class RecipeTable(Table):
    # name, cook_book (fk), page_number, notes):
    
    def __init__(self, name, rows, foreign_keys):
        super().__init__(name, rows, foreign_keys)


    @property
    def django_table(self):
        return Recipe


    def _query_row_exists(self, row):
        q = Recipe.objects.filter(title=row['name'])
        return q


    def _create_row(self, row):
        t = Recipe(
            name=row['name'],
            cook_book=row['cookbook'],
            page_number=row['page_number'],
            notes=row['notes']
        )
        return t


class RecipeRatingTable(Table):

    def __init__(self, name, rows, foreign_keys):
        super().__init__(name, rows, foreign_keys)


    @property
    def django_table(self):
        return RecipeRating


    def _query_row_exists(self, row):
        # Check if RecipeRating already in table
        # Get Diner and Recipe Object
        diner_obj = 1 #TODO: get actual diner
        recipe_obj = 1 #TODO: get actual recipe
        q = RecipeRating.objects.filter(recipe = recipe_obj, diner = diner_obj)
        return q


    def _create_row(self, row):
        r = Recipe(
            name=row['name'],
            cook_book=row['cookbook'],
            page_number=row['page_number'],
            notes=row['notes']
        )
        return r


class RecipeTypeTable(Table):

    def __init__(self, name, rows):
        super().__init__(name, rows)


    @property
    def django_table(self):
        return RecipeType


    def _query_row_exists(self, row):
        return super()._query_row_exists(row)


    def _create_row(self, row):
        return super()._create_row(row)


#------------------------------------------------
class MealDatabase():
    '''
    Class that knows the Meal Planner data model and relationships between tables
    '''

    _TABLE_AUTHOR = 'Author'
    _TABLE_COOKBOOK = 'Cookbook'
    _TABLE_DINER = 'Diner'
    _TABLE_RECIPE = 'Recipe'
    _TABLE_RECIPETYPE = 'RecipeType'
    _TABLE_RECIPE2TYPE = 'RecipeToType'
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
            'name': _TABLE_RECIPETYPE,
            'foreign_keys': []
        },
        {
            'name': _TABLE_RECIPE2TYPE,
            'foreign_keys': [
                {
                    'column': 'recipeid',
                    'related_table': _TABLE_RECIPE
                },
                {
                    'column': 'recipetypeid',
                    'related_table': _TABLE_RECIPETYPE
                }
            ]
        },
        {
            'name': _TABLE_MEAL,
            'foreign_keys': [
                {
                    'column': 'recipe',
                    'related_table': _TABLE_RECIPE
                }
            ]
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
        sorted_tables = []
        for t in self._TABLES:
            pass
        #   process tables so that tables with foreign key
        #   dependencies are loaded after tables they depend on

        # Iterate sorted table list
        for t in sorted_tables:
            pass
        #   Retrieve table data from source db
        #   Initialize table object with source data
        #   Check if table has foreign key dependencies
            if len(t.related_columns) > 0:
        #     if it does, send updated foreign key values (mapping)
                for rc in t.related_columns:
                    t.add_fk_mapping(self._get_table_by_name().pk_mapping)

        #   Load the table into django database


class PrimaryKeyMapping():

    def __init__(self, table: Table):
        #TODO: pass in the actual table class
        self._table = table
        self._rows = []
        for r in self._table.rows:
            mapping = {
                'source_pk': r['id'],
                'django_pk': r['d_id']    
            }
            self._rows.append(mapping)


    @property
    def rows(self):
        return self._rows


    @property
    def table_name(self) -> str:
        return self._table.name


    @property 
    def table(self):
        return self._table


    @property
    #TODO: have property that returns an instance of a row object from the django table
    def find_django_row(self, search_id):
        d_id = self.find_django_id(search_id)

        django_table = self.table.django_table

        return django_table.objects.get(pk=d_id)


    def find_django_id(self, search_id) -> int:
        for r in self.rows:
            if r['source_pk'] == search_id:
                return r['django_pk']
        return None
