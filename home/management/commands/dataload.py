import datetime
import sys
import os

parent_path = os.path.abspath("..") + "\\meal_planner"
sys.path.append(parent_path)
print(sys.path)
from cookbook.models import Author, Cookbook
from recipe.models import Diner, Recipe, RecipeRating, RecipeType
from meal.models import Meal

_TABLE_AUTHOR = 'Author'
_TABLE_COOKBOOK = 'Cookbook'
_TABLE_DINER = 'Diner'
_TABLE_RECIPE = 'Recipe'
_TABLE_RECIPETYPE = 'RecipeType'
_TABLE_RECIPE2TYPE = 'RecipeToType'
_TABLE_RECIPERATING = 'RecipeRating'
_TABLE_MEAL = 'Meal'

_FK_KEY = 'foreign_keys'
_NM_KEY = 'name'
_RT_KEY = 'related_table'
_CL_KEY = 'column'
_JT_KEY = 'is_junction'

_DJANGO_ID_COL = 'd_id'
_NV = 'NULL'  # NULL value


class TableFactory():

    def __init__(self):
        pass


    def createTable(self, data_model, table_def):
        table_obj = None
        table_name = table_def[_NM_KEY]

        if table_name.lower() == 'cookbook':
            table_obj = CookbookTable(data_model, table_def)
        elif table_name.lower() == 'author':
            table_obj = AuthorTable(data_model, table_def)
        elif table_name.lower() == 'diner':
            table_obj = DinerTable(data_model, table_def)
        elif table_name.lower() == 'recipe':
            table_obj = RecipeTable(data_model, table_def)
        elif table_name.lower() == 'meal':
            table_obj = MealTable(data_model, table_def)
        elif table_name.lower() == 'recipetype':
            table_obj = RecipeTypeTable(data_model, table_def)
        elif table_name.lower() == 'reciperating':
            table_obj = RecipeRatingTable(data_model, table_def)
        elif table_name.lower() == 'recipetotype':
            table_obj = RecipeToTypeTable(data_model, table_def)
        else:
            raise Exception(f'Table with name {table_name} does not exist in data model')

        return table_obj


class Table():

    def __init__(self, data_model, table_definition):
        name = table_definition[_NM_KEY]
        foreign_keys = table_definition[_FK_KEY]
        is_junction = True if _JT_KEY in table_definition and table_definition[_JT_KEY] else False
        
        self._datamodel = data_model
        self._name = name
        self._is_junction = is_junction
        self._rows = []
        self._related_columns = []
        for fk in foreign_keys:
            self._add_related_column(fk[_CL_KEY], fk[_RT_KEY])
        self._is_loaded = False


    @property
    def name(self):
        return self._name


    @property
    def rows(self):
        return self._rows


    @rows.setter
    def rows(self, rows):
        self._rows = rows

     
    @property 
    def related_columns(self):
        return self._related_columns


    @property
    def is_junction_table(self):
        return self._is_junction


    @property
    def is_loaded(self):
        return self._is_loaded


    @property
    def pk_mapping(self):
        pk_mapping = None
        if self.is_loaded:
            pk_mapping = PrimaryKeyMapping(self)
        return pk_mapping


    @property
    def django_table(self):
        # This method MUST be overridden in subclass
        return None


    def load(self):
        # Iterate rows
        for r in self.rows:

            # Check if record already in table
            q = self._query_row_exists(r)

            for rc in self.related_columns:
                # Use foreign key id to find actual object in django table
                fk_table = self._datamodel.get_table_by_name(rc[_RT_KEY])
                fk_mapping = fk_table.pk_mapping
                r[rc[_CL_KEY]] = fk_mapping.find_django_row(r[rc[_CL_KEY]])

            if not q:
                new_row = self._create_row(r)

                # Only save row and get djando id if NOT a junction table
                if not self.is_junction_table:
                    new_row.save()

                    # Get Django generated unique id
                    django_id = new_row.id
                    # Then add it to the data row being processed
                    r[_DJANGO_ID_COL] = django_id
            else:
                # Get the django id of the record IF AND ONLY IF table IS NOT a jucntion able
                if not self.is_junction_table:
                    # Assumption that only one record will be returned
                    r[_DJANGO_ID_COL] = q[0].id

        self._is_loaded = True


    def get_row_by_id(self, id):
        '''
        Queries rows for a given id using id from source table
        '''

        for r in self.rows:
            if r['id'] == id:
                return r
        
        raise Exception(f'Row with id {id} not found')


    def _query_row_exists(self, row):
        return None


    def _create_row(self, row):
        return None


    def _add_related_column(self, column_name, related_table):
        related_column = {
            _CL_KEY: column_name, 
            _RT_KEY: related_table, 
        }

        # check if related column already exists.
        # if it does replace it with new value
        found_match = False
        for rc in self._related_columns:
            if rc[_CL_KEY].lower() == related_column[_CL_KEY].lower():
                rc[_RT_KEY] = related_column[_RT_KEY]
                found_match = True
                break
        
        if not found_match:
            self._related_columns.append(related_column)


    def _get_related_table_by_fk(self, fk_column):
        '''
        Get a reference to a foreign key's table name
        '''

        for rc in self.related_columns:
            if fk_column.lower() == rc[_CL_KEY].lower():
                return rc[_RT_KEY]
        
        raise Exception(f'Invalid foreign key column "{fk_column}"')


class CookbookTable(Table):

    def __init__(self, data_model, table_definition):
        super().__init__(data_model, table_definition)


    @property
    def django_table(self):
        return Cookbook


    def _query_row_exists(self, row):
        query_value = row['title']
        q = Cookbook.objects.filter(title=query_value)
        return q


    def _create_row(self, row):
        r = Cookbook(
            title=row['title'],
            description=row['description'],
            author=row['author'],
            publish_date=row['published_date'],
            url=row['url'],
            edition=row['edition'],
            image=row['image']
        )
        return r


class AuthorTable(Table):

    def __init__(self, data_model, table_definition):
        super().__init__(data_model, table_definition)


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

    def __init__(self, data_model, table_definition):
        super().__init__(data_model, table_definition)


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
    
    def __init__(self, data_model, table_definition):
        super().__init__(data_model, table_definition)


    @property
    def django_table(self):
        return Recipe


    def _query_row_exists(self, row):
        q = Recipe.objects.filter(name=row['title'])
        return q


    def _create_row(self, row):
        t = Recipe(
            name=row['title'],
            cook_book=row['cook_book'],
            page_number=0 if row['page_number'] is None or row['page_number'] == _NV else row['page_number'],
            notes=row['notes']
        )
        return t


class RecipeRatingTable(Table):

    def __init__(self, data_model, table_definition):
        super().__init__(data_model, table_definition)


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
            cook_book=row['cook_book'],
            page_number=row['page_number'],
            notes=row['notes']
        )
        return r


class RecipeTypeTable(Table):

    def __init__(self, data_model, table_definition):
        super().__init__(data_model, table_definition)


    @property
    def django_table(self):
        return RecipeType


    def _query_row_exists(self, row):
        q = RecipeType.objects.filter(name = row['name'])
        return q


    def _create_row(self, row):
        r = RecipeType(name = row['name'])
        return r


class MealTable(Table):

    def __init__(self, data_model, table_definition):
        super().__init__(data_model, table_definition)


    @property 
    def django_table(self):
        return Meal

    
    def _query_row_exists(self, row):
        # format date to ensure in YYYY-MM-DD format
        date_obj = datetime.datetime.strptime(row['scheduled_date'], '%Y-%m-%d %H:%M:%S')
        scheduled_date = date_obj.strftime('%Y-%m-%d')
        q = Meal.objects.filter(scheduled_date = scheduled_date)
        return q


    def _create_row(self, row):
        # format date to ensure in YYYY-MM-DD format
        date_obj = datetime.datetime.strptime(row['scheduled_date'], '%Y-%m-%d %H:%M:%S')
        scheduled_date = date_obj.strftime('%Y-%m-%d')
        
        r = Meal(
            scheduled_date = scheduled_date,
            was_made = row['was_made'],
            recipe = row['recipe'],
            notes = '' if row['notes'] is None or row['notes'] == _NV else row['notes'] 
        )

        return r


class RecipeToTypeTable(Table):

    # refer to https://docs.djangoproject.com/en/dev/ref/models/relations/
    # to figure out how to establish M2M relationship

    def __init__(self, data_model, table_definition):
        super().__init__(data_model, table_definition)


    @property
    def django_table(self):
        return None


    def _query_row_exists(self, row):

        recipe_django_id = self._get_fk_table_django_id('recipeid', row)
        recipetype_django_row = self._get_fk_table_django_row('recipetypeid', row)

        q = recipetype_django_row.recipe_set.filter(pk=recipe_django_id).exists()
        
        return q
   
    
    def _create_row(self, row):

        recipetype_django_row = row['recipetypeid']
        recipe_django_row = row['recipeid']

        recipe_django_row.recipe_types.add(recipetype_django_row)
           
        # We're just creating an association between two rows, don't return anything   
        return None


    def _get_fk_table_django_id(self, fk_column_name, row):
        fk_table = self._datamodel.get_table_by_name(self._get_related_table_by_fk(fk_column_name))
        fk_table_row = fk_table.get_row_by_id(row[fk_column_name])
        fk_table_django_id = fk_table_row[_DJANGO_ID_COL]

        return fk_table_django_id


    def _get_fk_table_django_row(self, fk_column_name, row):

        fk_table = self._datamodel.get_table_by_name(self._get_related_table_by_fk(fk_column_name))
        fk_table_row = fk_table.get_row_by_id(row[fk_column_name])
        fk_table_django_id = fk_table_row[_DJANGO_ID_COL]
        fk_table_django_table = fk_table.django_table
        fk_table_django_row = fk_table_django_table.objects.get(pk=fk_table_django_id)

        return fk_table_django_row


#------------------------------------------------
class MealDatabase():
    '''
    Class that knows the Meal Planner data model and relationships between tables
    '''

    _TABLE_DEFS = [
        {
            _NM_KEY: _TABLE_AUTHOR,
            _FK_KEY : []
        },
        {
            _NM_KEY: _TABLE_COOKBOOK,
            _FK_KEY: [
                {
                    _CL_KEY: 'author',
                    _RT_KEY: _TABLE_AUTHOR
                }
            ]
        },
        {
            _NM_KEY: _TABLE_RECIPE,
            _FK_KEY: [
                {
                    _CL_KEY: 'cook_book',
                    _RT_KEY: _TABLE_COOKBOOK
                }
            ]
        },
        {
            _NM_KEY: _TABLE_DINER,
            _FK_KEY: []
        },
        {
            _NM_KEY: _TABLE_RECIPETYPE,
            _FK_KEY: []
        },
        {
            _NM_KEY: _TABLE_RECIPE2TYPE,
            _JT_KEY: True,
            _FK_KEY: [
                {
                    _CL_KEY: 'recipeid',
                    _RT_KEY: _TABLE_RECIPE
                },
                {
                    _CL_KEY: 'recipetypeid',
                    _RT_KEY: _TABLE_RECIPETYPE
                }
            ]
        },
        {
            _NM_KEY: _TABLE_MEAL,
            _FK_KEY: [
                {
                    _CL_KEY: 'recipe',
                    _RT_KEY: _TABLE_RECIPE
                }
            ]
        }        
    ]

    def __init__(self, database_connection):
        self._db_conn = database_connection
        
        # sort tables by foreign key dependencies
        self._sort_tables()

        # Initialize (empty) table objects
        self._tables = []
        for t in self._TABLE_DEFS:
            table = TableFactory().createTable(self, t)
            self._tables.append(table)


    @property
    def database_connection(self):
        return self._db_conn


    def get_table_by_name(self, table_name):
        for t in self._tables:
            if t.name.lower() == table_name.lower():
                return t
        raise Exception(f'Table "{table_name}" not found')


    def load(self):
        '''
        Load the Django database
        '''

        # Iterate sorted table list
        for t in self._tables:
            print(f'Processing {t.name}...')
            #   Retrieve table data from source db
            print('Getting data from source...')
            rows = self.read_table_from_source(t.name)
            #   Initialize table object with source data
            t.rows = rows
            #   Load the table into django database
            print('Loading...')
            t.load()


    def read_table_from_source(self, table_name):

        cursor = self.database_connection.cursor()
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


    def _sort_tables(self):
        # Sort tables so those with foreign key dependencies are 
        # loaded after their dependencies

        def _t1_dep_t2(t1, t2):
            # check if table 1 (t1) is dependent on table 2 (t2)
            fky = _FK_KEY

            if len(t1[fky]) == 0:
                return False
            
            for fk in t1[fky]:
                if fk[_RT_KEY] == t2[_NM_KEY]:
                    return True

            return False

        tl = self._TABLE_DEFS
        fky = _FK_KEY
        n = len(tl)

        for i in range(n):

            for j in range(0, n-i-1):
                if len(tl[j][fky]) > len(tl[j+1][fky]):
                    tl[j], tl[j+1] = tl[j+1], tl[j]
                elif _t1_dep_t2(tl[j], tl[j+1]):
                    tl[j], tl[j+1] = tl[j+1], tl[j]


class PrimaryKeyMapping():

    def __init__(self, table: Table):
        self._table = table
        self._rows = []
        for r in self._table.rows:
            mapping = {
                'source_pk': r['id'],
                'django_pk': r[_DJANGO_ID_COL]    
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


    def find_django_row(self, search_id):
        if search_id == 0:
            # there is not associated foreign object, so return None
            return None

        d_id = self.find_django_id(search_id)

        django_table = self.table.django_table

        return django_table.objects.get(id=d_id)


    def find_django_id(self, search_id) -> int:
        for r in self.rows:
            if r['source_pk'] == search_id:
                return r['django_pk']
        return None
