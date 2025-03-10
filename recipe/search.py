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
    RECIPE:   searches on Recipe Name
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
    'AUTHOR:',
    'RECIPE:',
]

TIME_KEYWORD_TOKENS = [
    'BEFORE:',
    'AFTER:',
    'OLDER:',
]


class Search:
    '''
    Class that manages searching for recipes
    '''
    '''
    Class that manages searching for recipes
    '''

    def __init__(self, search_string: str):

        # Tokens: elements used for searching, separated by spaces in search_string
        # Keyword tokens: special tokens used to focus search on specific properties

        self._tokens = search_string.split(' ')
        self._keywords = dict.fromkeys(
            [k.upper() for k in self._tokens if k.upper() in KEYWORD_TOKENS])
        self._time_keywords = dict.fromkeys(
            [k.upper() for k in self._tokens if k.upper() in TIME_KEYWORD_TOKENS])
        self._freetokens = self._parse_keywords(self.tokens)

    @property
    def tokens(self):
        '''
        Return list of search tokens
        '''
        '''
        Return list of search tokens
        '''
        return [t.upper() for t in self._tokens]

    @property
    def free_tokens(self):
        '''
        Return list of free search tokens
        '''
        '''
        Return list of free search tokens
        '''
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
        '''
        Return list of time filtering keywords
        '''
        '''
        Return list of time filtering keywords
        '''

        return self._time_keywords[keyword]



    def find(self):
        '''
        Execute the query based on the tokens provided
        '''

        # Build query
        # For Recipe Types

        # Build query strings of search values
        # - a search value is a token that is NOT a keyword
        # - search values (tokens) that are associated with a keyword are only used to search
        #   for that keyword's associated table
        # - free tokens are assigned to all keywords

        # Create dictionaries for search values for all keywords with
        # initial value of an empty list
        keyword_searches = {key: [] for key in KEYWORD_TOKENS} 

        # Go through all tokens
        for token in self.tokens:
            # if token is a keyword, then extract the search values
            if token in self.keywords:
                search_values = self.keyword_search_values(token)
                keyword_searches[token] = search_values  # type: ignore

            # Else if token is a free token, add it to all keyword searches
            else:
                if token in self.free_tokens:
                    for key in keyword_searches:
                        keyword_searches[key].append(token)
        # [end] for token

        # Build queries and search for matches, based on
        # contents of keyword_searches dictionary

        #TODO: Would it be better to initialize as an empty Django result set?
        #TODO: Would it be better to initialize as an empty Django result set?
        recipe_result = None

        for keyword in keyword_searches:
            for value in keyword_searches[keyword]:
                if keyword == "TYPE:":
                    recipe_qs = Recipe.objects.filter(
                        recipe_types__name__iexact=value)
                elif keyword == "COOKBOOK:":
                    recipe_qs = Recipe.objects.filter(
                        cook_book__title__icontains=value)
                elif keyword == "AUTHOR:":
                    recipe_qs = Recipe.objects.filter(
                        Q(cook_book__author__first_name__icontains=value) | Q(cook_book__author__last_name__icontains=value))
                elif keyword == "RECIPE:":
                    recipe_qs = Recipe.objects.filter(
                        name__icontains=value)
                else:
                    # create empty query set by default
                    recipe_qs = Recipe.objects.none
                # [end] if keyword

                # Combine individual recipe type querysets into one big queryset
                if recipe_result is None:
                    recipe_result = recipe_qs
                else:
                    recipe_result = recipe_result.union(recipe_qs)
                # [end] if recipe_result
            # [end] for value
        # [end] for keyword            

        # Last search is to filter all results by the time filters
        for keyword in self.time_keywords:
            time_search_values = self.keyword_search_values(keyword)

            # TODO: implement time filters

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


    def _parse_date(self, date_string):
        for fmt in ('%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y', '%d-%b-%Y'):
            try:
                date = datetime.datetime.strptime(date_string, fmt).date()
                return date
            except ValueError:
                pass
        return None
