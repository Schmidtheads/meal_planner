'''
  Name       :  Search.py
  Description:  Module that will search for recipes
                Given a string of search tokens
                which can use keywords to query specific values
  Author     :  M. Schmidt
  Date       :  29-Sep-2021

  Acceptable keywords are:
  COOKBOOK:  AUTHOR:  BEFORE:  AFTER:  OLDER:  TYPE:

  Note: only one of BEFORE, AFTER or OLDER can be specified
  (first come, first served), subsequent time slicing will
  be ignored.
'''

import datetime

from django.db.models import Q
from .models import Recipe

KEYWORD_TOKENS = [
    'TYPE:',
    'COOKBOOK:',
    'AUTHOR:'
    ]

TIME_KEYWORD_TOKENS = [
    'BEFORE:',
    'AFTER:',
    'OLDER:'
]

class Search:

    def __init__(self, search_string):

        # Tokens: elements used for searching, separated by spaces in search_string
        # Keyword tokens: special tokens used to focus search on specific properties

        self._tokens = search_string.split(' ')
        self._keywords = dict.fromkeys([k.upper() for k in self._tokens if k.upper() in KEYWORD_TOKENS])
        self._parse_keywords()

        self._time_keywords = dict.fromkeys([k.upper() for k in self._tokens if k.upper() in TIME_KEYWORD_TOKENS])
        self._parse_time_keywords()

        
    @property
    def tokens(self):
        return [t.upper() for t in self._tokens]


    @property
    def keywords(self):
        '''
        Return list of keyword tokens used in this search
        '''
        
        return list(self._keywords.keys())


    def keyword_search_values(self, keyword):
        '''
        Return a list of search values for a given token
        '''
        
        return self._keywords[keyword]


    @property
    def time_keywords(self):
        '''
        Return list of keyword tokens used for time searching
        '''

        return list(self._time_keywords.keys())


    def time_filter_date(self, keyword):

        return self._time_keywords[keyword]


    def find(self):
        # Excecute the query based on the tokens provided
        

        # Build query
        # For Recipe Types

        recipe_result = None

        # Search keyword tokens first
        for keyword in self.keywords:
            search_values = self.keyword_search_values(keyword)
        
            for value in search_values:
                if keyword == "TYPE:":
                    recipe_qs = Recipe.objects.filter(recipe_types__name__iexact=value)
                elif keyword == "COOKBOOK":
                    recipe_qs = Recipe.objects.filter(cook_book__name__icontains=value)
                elif keyword == "AUTHOR:":
                    recipe_qs = Recipe.objects.filter(
                        Q(cook_book__author__first_name__icontains=value) | Q(cook_book__author__last_name__icontains=value))
                #end if keyword

                # Combine individual recipe type querysets into one big queryset
                if recipe_result is None:
                    recipe_result = recipe_qs
                else:
                    recipe_result = recipe_result | recipe_qs
            #end for value
            
        #end for keyword

        #TODO: implement non-keyword searches

        # Last search is to filter all results by the time filters
        for keyword in self.time_keywords:
            time_search_values = self.time_search_values(keyword)
            
            #TODO: implement time filters
            
        # test - loop through recipe type queryset to get recipes
        for r in recipe_result:
            print(r.name)

        # Get recipe related information
        return recipe_result


    def _parse_keywords(self):
        # locate keywords in token list and get search
        # values for token (if any!)

        # Keep list of tokens that have NOT been processed.
        # Those that are left over are "free" tokens and will
        # be used to search against ALL criteria.
        tokens_not_processed = self.tokens

        for k in self.keywords:
            token_idx = self.tokens.index(k)
            tokens_not_processed.remove(k)

            # if search token not at end of list, grab next token of search values
            # keyword can have muliple search values, if comma separated (no spaces!)
            search_values = ''
            if token_idx < len(self.tokens):
                next_token = self.tokens[token_idx + 1]

                # Make sure the next token is not a keyword
                # if it is, then current keyword is invalid and will be ignored

                if not next_token.upper() in KEYWORD_TOKENS:
                    search_values = next_token.split(',')
                    tokens_not_processed.remove(next_token)

                    # Add search values for keyword to class property
                    self._keywords[k] = search_values


    def _parse_time_keywords(self):
        '''
        Parse the time keywords in the search text to extract dates
        '''

        for k in self.time_keywords:
            # check if datetime is valid
            date = self._parse_date(self.time_filter_date(k))

            # if date invalid, remove time keyword
            if date is None:
                del self._time_keywords[k]
            else:
                self._time_keywords[k] = date


    def _parse_date(self, date_string):
        for fmt in ('%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y', '%d-%b-%Y'):
            try:
                date = datetime.datetime.strptime(date_string, fmt).date()
                return date
            except ValueError:
                pass
        return None

