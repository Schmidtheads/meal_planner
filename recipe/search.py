'''
  Name       :  Search.py
  Description:  Module that will search for recipes
                Given a string of search tokens
                which can use keywords to query specific values
  Author     :  M. Schmidt
  Date       :  29-Sep-2021

  Acceptable keywords are:
    COOKBOOK: searches on title
    AUTHOR:   searches on firstname or lastname
    TYPE:     searches on Recipe Tags
    RATING:   searches on Recipe rating
    BEFORE:   searches on Meal date before given date
    AFTER:    searches on Meal date after given date
    OLDER:    searches on Meal date older than given date OR
              older than give time period: #[unit] where
                # is an integer
                [unit] is M (months), W (weeks), D (days)

  Any tokens not associated with a keyword will be searched against all criteria.
  Search criteria include:
    Cookbook:
        -Author [firstname, lastname]
        -Title
        -Descripton
    Recipe:
        -Name
        -Recipe Tags
        
  Note: only one of BEFORE, AFTER or OLDER can be specified
  (first come, first served), subsequent time slicing will
  be ignored.
'''

import copy
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
        self._time_keywords = dict.fromkeys([k.upper() for k in self._tokens if k.upper() in TIME_KEYWORD_TOKENS])
        self._freetokens = self._parse_keywords(self.tokens)


    @property
    def tokens(self):
        return [t.upper() for t in self._tokens]


    @property
    def free_tokens(self):
        return [t.upper() for t in self._freetokens]

    
    @property
    def keywords(self):
        '''
        Return list of keyword tokens used in this search
        '''

        return list(self._keywords.keys())


    @property
    def time_keywords(self):
        '''
        Return list of keyword tokens used for time searching
        '''

        return list(self._time_keywords.keys())


    @property
    def all_keywords(self):
        '''
        Return list of keyword tokens and time keycodes used in this search
        '''
        
        return list(self._keywords.keys()) + list(self._time_keywords.keys())


    def keyword_search_values(self, keyword):
        '''
        Return a list of search values for a given token

        @param keyword: keyword name for which to retreive search values
        @return: search value as either a list or datetime
        '''
        
        all_keywords = {**self._keywords, **self._time_keywords}

        return all_keywords[keyword]


    def time_filter_date(self, keyword):

        return self._time_keywords[keyword]


    def find(self):
        '''
        Execute the query based on the tokens provided
        '''

        # Build query
        # For Recipe Types

        recipe_result = None  #TODO Would it be better to initialize as an empty Django result set?

        # Search keyword tokens first
        for keyword in self.keywords:
            search_values = self.keyword_search_values(keyword)
        
            # Add tokens that aren't associated with a keyword
            search_values = search_values + self.free_tokens

            for value in search_values:
                if keyword == "TYPE:":
                    recipe_qs = Recipe.objects.filter(recipe_types__name__iexact=value)
                elif keyword == "COOKBOOK:":
                    recipe_qs = Recipe.objects.filter(cook_book__name__icontains=value)
                elif keyword == "AUTHOR:":
                    recipe_qs = Recipe.objects.filter(
                        Q(cook_book__author__first_name__icontains=value) | Q(cook_book__author__last_name__icontains=value))
                #end if keyword

                # Combine individual recipe type querysets into one big queryset
                if recipe_result is None:
                    recipe_result = recipe_qs
                else:
                    recipe_result = recipe_result.union(recipe_qs)
                    #recipe_result = recipe_result | recipe_qs
                    #recipe_result = recipe_result.distinct()  # remove duplicates
            #end for value
            
        #end for keyword

        #TODO: implement non-keyword searches
        #  Maybe identify non-keyword terms and append to each keyword search above to
        #  reduce number of queries carried out.
        #  Perform query against all criteria (see file header above), skipping
        #  any criteria already search in keyword search. 

        # Last search is to filter all results by the time filters
        for keyword in self.time_keywords:
            time_search_values = self.keyword_search_values(keyword)
            
            #TODO: implement time filters
            
        # test - loop through recipe type queryset to get recipes
        if not recipe_result is None:
            for r in recipe_result:
                print(r.name)

        # Get recipe related information
        return recipe_result


    def _parse_keywords(self, tokens):
        '''
        Locate keywords in token list and get search values for token (if any!)

        @param tokens: list of tokens to parse for searching
        '''

        # Keep list of tokens that have NOT been processed.
        # Those that are left over are "free" tokens and will
        # be used to search against ALL criteria.
        tokens_not_processed = copy.deepcopy(tokens)

        for k in self.all_keywords:
            token_idx = tokens.index(k)
            tokens_not_processed.remove(k)

            # if search token not at end of list, grab next token of search values
            # keyword can have muliple search values, if comma separated (no spaces!)
            search_values = ''
            if token_idx < len(tokens):
                next_token = tokens[token_idx + 1]

                # Make sure the next token is not a keyword
                # if it is, then current keyword is invalid and will be ignored

                if not next_token.upper() in self.keywords:

                    # only split by , if current keyword is not a time keyword
                    if k not in self._time_keywords:    
                        # Split search values by comma and add values for
                        # keyword to class property
                        self._keywords[k] = next_token.split(',')
                    else:
                        date = self._parse_date(next_token)
                        # if date is invalid, raise error
                        if date is None:
                            raise Exception("Invalid date format")
                        self._time_keywords[k] = date

                    tokens_not_processed.remove(next_token)

        return tokens_not_processed


    def _parse_time_keywords(self, tokens):
        '''
        *** DEPRECATED ***
        Parse the time keywords in the search text to extract dates

        @param tokens: list of tokens to parse for time searching
        @return: list of tokens not used for time searching
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

