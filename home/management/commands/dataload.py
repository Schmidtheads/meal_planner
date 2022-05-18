import sys
import os

parent_path = os.path.abspath("..") + "\\meal_planner"
sys.path.append(parent_path)
print(sys.path)
from cookbook.models import Author, Cookbook
from recipe.models import Diner, Recipe, RecipeRating, RecipeType


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

    def __init__(self, name, rows):
        self._name = name
        self._rows = rows

    @property
    def name(self):
        return self._name

    @property
    def rows(self):
        return self._rows


    def get_related_ids(self, related_table, related_column):
        pass

        # for each row:
        #  get the d_id of the related table,
        #  then update the related_column in the current table


class CookbookTable(Table):

    def __init__(self, name, rows):
        super().__init__(name, rows)


    def load(self):
        # title, descr, author_pk, pdate, url=None, edition=None, image_path=None):

        # Iterate rows
        for r in self.rows:

            # Check if Cookbook already in table
            q = Cookbook.objects.filter(title=r['title'])

            if not q:
                c = Cookbook(
                    title=r['title'],
                    description=r['description'],
                    author=r['author'],
                    published_date=r['published_date'],
                    url=r['url'],
                    edition=r['edition'],
                    image=r['image']
                )
                c.save()

                # Get Django generated unique id
                django_id = c.id
                # Then add it to the data row being processed
                r['d_id'] = django_id
            else:
                c = None


class AuthorTable(Table):

    def __init__(self, name, rows):
        super().__init__(name, rows)


    def load(self):

        # Iterate rows of table
        for r in self.rows:

            # Check if Author already in table
            q = Author.objects.filter(first_name = r['first_name'], last_name = r['last_name'])

            if not q:
                a = Author(first_name = r['first_name'], last_name = r['last_name'])
                a.save()

                # Get Django generated unique id
                django_id = a.id
                # Then add it to the data row being processed
                r['d_id'] = django_id
            else:
                a = None

        return a


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

    def __init__(self, name, rows):
        super().__init__(name, rows)


    def load(self):
        # title, descr, author_pk, pdate, url=None, edition=None, image_path=None):

        # Iterate rows
        for r in self.rows:

            # Check if Recipe already in table
            q = Recipe.objects.filter(title=r['name'])

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
