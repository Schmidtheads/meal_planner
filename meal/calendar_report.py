'''
Title       : calendar_report.py
Description : Meal Plan calendar PDF generator
Author      : M. Schmidt
Date        : 26-Mar-2023

Notes:
  To use, instantiate the MonthlyMealPlan class.
  Then use the print_page() to generate the meal plan in PDF format.
'''

import calendar
from datetime import datetime
from fpdf import FPDF
from textwrap import wrap


DAYS_OF_WEEK = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']


class MonthlyMealPlan(FPDF):
    '''
    Class to Create a Monthly Meal Plan
    '''

    def __init__(self, month, meals, weeks_to_print: list=[], print_meals_only: bool=False):
        '''
        Constructor
        @param month: (string) year and month of calendar (YYYY-MM)
        @param meals: (dict) meal data to use in calendar
        @param weeks_to_print: (list) list of week numbers (0 based) to print
        @param print_meals_only: (bool) Flag to indicate if only meal information to be printed
        '''
        super().__init__('L', 'pt', 'Letter')
        self.WIDTH = 792
        self.HEIGHT = 612
        self.CALENDAR_WIDTH = self.WIDTH * .92
        self.CALENDAR_HEIGHT = self.HEIGHT * .90
        self.HEADER_HEIGHT = self.HEIGHT / 20.4 
        self.DATE_HEIGHT = self.HEIGHT / 30.6
        self.DAYS = 7
        self.WEEKS = 5
        # Ratio of calendar day each "section" occupies
        self.r0p = 0.15
        self.r1p = 0.70
        self.r2p = 0.15

        if isinstance(month, str):
            self.calendar_month = datetime.strptime(month, '%Y-%m')
        elif isinstance(month, datetime):
            self.calendar_month = month

        self._meals = meals
        self.weeks_to_print = [0,1,2,3,4,5] if weeks_to_print == [] else weeks_to_print

        self.only_meals = print_meals_only

        self.out_filepath = None
        self.out_type = 'F'

        calendar.setfirstweekday(calendar.SUNDAY)


    @property
    def output_filepath(self):
        return self.out_filepath
    

    @output_filepath.setter
    def output_filepath(self, value):
        self.out_filepath = value


    @property
    def output_type(self):
        return self.out_type
    
    
    @output_type.setter
    def output_type(self, value):
        value = value.upper()
        if value != 'S':
            value = 'F'

        self.out_type = value


    def calendar_days(self, month=None) -> list:
        '''
        Returns array of meal plan calendar days
        '''
        month = self.month if month is None else month
        calendar_days = calendar.monthcalendar(self.year, month)
        return calendar_days


    @property 
    def grid_days(self) -> list:
        '''
        Returns array of meal plan days for grid (include partials of previous and next month)
        '''

        grid_days = self.calendar_days()
        for idx, w in enumerate(grid_days):
            grid_days[idx] = [f'{self.month}:{d}' if d != 0 else d for d in w]
        previous_month = self.calendar_days(self.month -1)
        next_month = self.calendar_days(self.month +1)

        for d in range(7):
            if grid_days[0][d] == 0:
                grid_days[0][d] = f'{self.month -1}:{previous_month[-1][d]}'

        for d in range(7):
            if grid_days[-1][d] == 0:
                grid_days[-1][d] = f'{self.month +1}:{next_month[0][d]}'

        return grid_days


    @property
    def month(self) -> int:
        '''
        Return meal plan month as number
        '''

        return int(self.calendar_month.month)


    @property
    def month_name(self):
        '''
        Returns meal plan month
        '''
        return self.calendar_month.strftime('%B')


    @property
    def year(self) -> int:
        '''
        Returns meal plan year
        '''
        return int(self.calendar_month.strftime('%Y'))


    @property
    def meals(self):
        '''
        Returns meals list
        '''
        return self._meals


    def print_page(self):
        '''
        Creates the Meal Plan report page.
        '''
        self.add_page()
        self.page_body()
        # May want to validate that out_filepath is an actual file
        if not self.output_filepath is None:
            # from https://stackoverflow.com/questions/56639834/pyfpdf-returns-a-blank-pdf-after-encoding-as-a-byte-string
            if self.output_type == 'S':
                return self.output(self.out_filepath, 'S').encode('latin-1')
            else:
                return self.output(self.out_filepath, 'F')

        return None
    

    def header(self):
        if not self.only_meals:
            self.set_font('Arial', 'B', 22)

            self.set_text_color(0,96,200)
            self.cell(self.WIDTH, self.HEADER_HEIGHT, f'Meal Plan - {self.month_name} {self.year}', align='C')
            self.ln()


    def page_body(self):
        '''
        Creates page body of report
        '''

        # create calendar grid
        if not self.only_meals:
            self._build_week_header()
        for w in range(self.WEEKS):
            self._build_week(w)


    def _build_week_header(self):
        '''
        Create weekday headers for calendar
        '''

        self.set_font('Arial', 'B', 10)
        self.set_text_color(34, 84, 8)
        self.set_fill_color(232, 212, 155)

        for day in DAYS_OF_WEEK:
            ln = 1 if day == DAYS_OF_WEEK[-1] else 0
            self.cell(
                self.CALENDAR_WIDTH / self.DAYS,
                self.DATE_HEIGHT,
                txt = day,
                align = 'C',
                border = 1,
                ln=ln,
                fill=True
            )


    def _get_meal_for_day(self, month: int, day: int):
        '''
        Returns the meal information for a given month and day
        @param month: (int) month as a integer between 1 and 12
        @param day: (int) day as an integer between 1 and 31
        @return: (dict) meal information
        '''
        month = int(month)
        day = int(day)

        return next((meal for meal in self._meals if meal['scheduled_date'][-5:] == f'{month:02}-{day:02}'), None)


    def _build_week(self, week_no: int):
        '''
        Build a week as seven columns of three row
        @param week_no: (int) week of month
        '''

        week_of_month = self.grid_days[week_no]

        cell_top = -1
        cur_x = -1
        cur_y = -1

        for r in range(3):

            for d in range(self.DAYS):
                month, day_of_month = week_of_month[d].split(':')
                meal = self._get_meal_for_day(month, day_of_month)
                if meal is not None and week_no in self.weeks_to_print:
                    recipe = meal['recipe_name']
                    cookbook_abbr = meal['abbr'] if 'abbr' in meal and meal['abbr'] != 'Unk' else ''
                    page = f'p.{meal["page"]}' if 'page' in meal and meal['page'] != 0 else ''
                else:
                    recipe = ''
                    cookbook_abbr = ''
                    page = ''

                ln = 1 if d == self.DAYS - 1 else 0

                # Each calendar day is made of three sections
                # r=0: day of month
                # r=1: recipe name
                # r=2: cookbook and page
                # Process each section below
                if r == 0:
                    cell_top = self.get_y()
                    self._print_calendar_day(day_of_month, month, ln)
                    cur_y = self.get_y()
                elif r == 1:
                    #recipe
                    cur_x = 28.35 + (self.CALENDAR_WIDTH / self.DAYS) * d
                    self._print_recipe_name(cur_x, cur_y, recipe, d, ln)
                else:
                    #cookbook and page no
                    self._print_cookbook(cell_top, cookbook_abbr, page, d, ln)


    def _print_calendar_day(self, day_of_month: int, month: int, ln: int):
        '''
        Output the day of month
        @param day_of_month: day of month as integer
        @param month: month of year as integer
        @param ln: line wrapping flag, 0 for stay on this line, 1 for next line        
        '''

        self.set_font('Times', 'I', 8)
        self.set_text_color(17, 120, 125)
        # month abbr if not current month
        c_border = 0 if self.only_meals else 'LT'
        if not self.only_meals:
            month_label = '' if int(month) == self.month else calendar.month_abbr[int(month)]
        else:
            month_label = ''
        self.cell(
            (self.CALENDAR_WIDTH / self.DAYS) / 2,
            (self.CALENDAR_HEIGHT / self.WEEKS) * self.r0p,
            txt = month_label,
            align = 'L',
            border = c_border,
            ln=0
        )
        # day of month
        c_border = 0 if self.only_meals else 'TR'
        day_label = '' if self.only_meals else f'{day_of_month}'
        self.cell(
            (self.CALENDAR_WIDTH / self.DAYS) / 2,
            (self.CALENDAR_HEIGHT / self.WEEKS) * self.r0p,
            txt = day_label,
            align = 'R',
            border = c_border,
            ln=ln
        )


    def _print_recipe_name(self, x: float, y: float, recipe_name: str, ln: int=0, c_border=0):
        '''
        Outputs a recipe to calendar, wrapping text if required
        @param x: curent abscissa location
        @param y: current ordinate location
        @param recipe_name: name of recipe to print
        @param ln: line wrapping flag, 0 for stay on this line, 1 for next line
        @param c_border: border style
        '''

        font_height = 10.0
                 
        self.set_font('Arial', '', 10)
        c_border = 0 if self.only_meals else 'LR'
        self.set_text_color(0, 0, 0)

        sw = self.get_string_width(recipe_name)
        cw = self.CALENDAR_WIDTH / self.DAYS
         
        rcl = [''] if len(recipe_name) == 0 else wrap(recipe_name, int(len(recipe_name) * (cw / sw)))

        self.set_y(y)
        self.set_x(x)
        self.cell(
            (self.CALENDAR_WIDTH / self.DAYS),
            (self.CALENDAR_HEIGHT / self.WEEKS) * self.r1p,
            align='L',
            border=c_border,
            ln=ln
        )

        for c, value in enumerate(rcl):
            y_offset = c * font_height 
            #self.set_xy(x, y + y_offset)
            self.set_y(y + y_offset)
            self.set_x(x)
            self.write(30, value)


    def _print_cookbook(self, cell_top: float, cookbook_abbr: str, page: int, d: int, ln: int):
        '''
        Output cookbook information
        @param cell_top: ordinate value of cell top
        @param cookbook_abbr: abbreviation of cookbook title
        @param page: page number of recipe
        @param d: day of week as integer
        @param ln: line wrapping flag, 0 for stay on this line, 1 for next line 
        '''
        self.set_font('Arial', 'I', 8)
        c_border = 0 if self.only_meals else 'LB'
        self.set_y(cell_top + (self.CALENDAR_HEIGHT / self.WEEKS) * self.r1p) 
        self.set_x(28.35 + (self.CALENDAR_WIDTH / self.DAYS) * d)
        self.cell(
            (self.CALENDAR_WIDTH / self.DAYS) / 2,
            (self.CALENDAR_HEIGHT / self.WEEKS) * self.r2p,
            txt = f'{cookbook_abbr}',
            align = 'L',
            border = c_border,
            ln=0
        )
        c_border = 0 if self.only_meals else 'BR'
        self.cell(
            (self.CALENDAR_WIDTH / self.DAYS) / 2,
            (self.CALENDAR_HEIGHT / self.WEEKS) * self.r2p,
            txt = f'{page}',
            align = 'R',
            border = c_border,
            ln=ln
        )
