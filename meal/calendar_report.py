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
from dataclasses import dataclass
from fpdf import FPDF


DAYS_OF_WEEK = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

@dataclass(frozen=True)
class FontConfig:
    family: str
    style: str
    size: int

    @property
    def line_height(self) -> float:
        """Returns the 1.2x line height in inches."""
        return (self.size / 72) * 1.2


@dataclass(frozen=True)
class AppFonts:
    day: FontConfig
    recipe: FontConfig
    notes: FontConfig
    cookbook: FontConfig


class MonthlyMealPlan(FPDF):
    '''
    Class to Create a Monthly Meal Plan
    '''

    FONTS = AppFonts(
        day=FontConfig(family='Times', style='BI', size=8),
        recipe=FontConfig(family='Arial', style='', size=10),
        notes=FontConfig(family='Times', style='', size=6),
        cookbook=FontConfig(family='Arial', style='I', size=8)
    )

    def __init__(self, month, meals, weeks_to_print: list=[], print_meals_only: bool=False, print_notes: bool=True):
        '''
        Constructor
        @param month: (string) year and month of calendar (YYYY-MM)
        @param meals: (dict) meal data to use in calendar
        @param weeks_to_print: (list) list of week numbers (0 based) to print
        @param print_meals_only: (bool) Flag to indicate if only meal information to be printed
        @param print_notes: (bool) Flag to indicate if meal notes are printed
        '''
        # orientation = 'L'andscape 'P'ortrait
        # units = 'pt' or 'in'
        super().__init__(orientation='L', unit='in', format='Letter')
        self.margin_x = 0.5
        self.margin_y = 0.5

        self.WIDTH = 11 #792   # Page width
        self.HEIGHT = 8.5 #612 # Page height
        self.CALENDAR_WIDTH = self.WIDTH * .92
        self.CALENDAR_HEIGHT = self.HEIGHT * .90
        self.HEADER_HEIGHT = 0.5 # self.HEIGHT / 20.4 # Title Header Height 
        self.WEEKDAY_HEADER_HEIGHT =  0.3 #self.HEIGHT / 30.6
        self.DAYS = 7
        self.WEEKS = 5
        # Ratio of calendar day each "section" occupies
        self.r0p = 0.1 #0.15
        self.r1p = 0.6 #0.70
        self.r2p = 0.2
        self.r3p = 0.1 #0.15

        if isinstance(month, str):
            self.calendar_month = datetime.strptime(month, '%Y-%m')
        elif isinstance(month, datetime):
            self.calendar_month = month

        self._meals = meals
        self.weeks_to_print = [0,1,2,3,4,5] if weeks_to_print == [] else weeks_to_print

        self.only_meals = print_meals_only
        self.meal_notes = print_notes

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


    def calendar_days(self, month=None, year=None) -> list:
        '''
        Returns array of meal plan calendar days
        '''
        month = self.month if month is None else month
        year = self.year if year is None else year
        calendar_days = calendar.monthcalendar(year, month)

        # edge case: February in non-leap year with first day of month on Sunday
        # results in only 4 rows in calendar (where 5 is expected)
        # In this case add extra row of zeros
        if len(calendar_days) == 4:
            calendar_days.append([0,0,0,0,0,0,0])
            
        return calendar_days


    @property 
    def grid_days(self) -> list:
        '''
        Returns array of meal plan days for grid (include partials of previous and next month)
        '''

        grid_days = self.calendar_days()
        for idx, w in enumerate(grid_days):
            grid_days[idx] = [f'{self.month}:{d}' if d != 0 else d for d in w]
        p_month_no, p_month_yr = self._get_previous_month(self.month)
        previous_month = self.calendar_days(p_month_no, p_month_yr)
        n_month_no, n_month_yr = self._get_next_month(self.month)
        next_month = self.calendar_days(n_month_no, n_month_yr)

        for d in range(7):
            if grid_days[0][d] == 0:
                grid_days[0][d] = f'{p_month_no}:{previous_month[-1][d]}'

        for d in range(7):
            if grid_days[-1][d] == 0:
                grid_days[-1][d] = f'{n_month_no}:{next_month[0][d]}'

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
        self.page_body()  # Call to build content -> it happens here
        # May want to validate that out_filepath is an actual file
        if not self.output_filepath is None:
            # from https://stackoverflow.com/questions/56639834/pyfpdf-returns-a-blank-pdf-after-encoding-as-a-byte-string
            if self.output_type == 'S':
                return self.output(self.out_filepath, 'S').encode('latin-1')
            else:
                return self.output(self.out_filepath, 'F')

        return None
    

    def header(self):
        # if printing meals only, hide header text
        header_text = '' if self.only_meals else f'Meal Plan - {self.month_name} {self.year}'
            
        self.set_font('Arial', 'B', 22)

        self.set_text_color(0,96,200)
        self.cell(self.WIDTH, self.HEADER_HEIGHT, header_text , align='C')
        self.ln()


    def page_body(self):
        '''
        Creates page body of report
        '''

        # create calendar grid
        #if not self.only_meals:
        self._build_week_header()

        # recalculate usable page height accountinf for title and weekday header
        usable_height = self.h - (2 * self.margin_y) - self.HEADER_HEIGHT

        self.DAY_CELL_WIDTH = (self.w - 2 * self.margin_x) / self.DAYS
        self.DAY_CELL_HEIGHT = usable_height / self.WEEKS
        self.DAY_CELL_START_Y = self.get_y()

        # Disable automatic page breaks
        # - prevents printing of cookbook and page triggering new page
        self.set_auto_page_break(False)
        
        for w in range(self.WEEKS):
            self._build_week(w)


    def _build_week_header(self):
        '''
        Create weekday headers for calendar
        '''

        self.set_font('Arial', 'B', 10)
        self.set_text_color(34, 84, 8)
        self.set_fill_color(232, 212, 155)

        # if printing only meals, hide borders and fill colour
        fill_flag = False if self.only_meals else True
        border_flag = 0 if self.only_meals else 1
        
        for i,day in enumerate(DAYS_OF_WEEK):
            #[delete] ln = 1 if day == DAYS_OF_WEEK[-1] else 0

            # if printing only meals, hide day of week header
            print_day = '' if self.only_meals else day

            self.set_xy(self.margin_x + i *(self.w -2 * self.margin_x) / 7, self.get_y())
            self.cell(
                (self.w -2 * self.margin_x) / self.DAYS,
                self.WEEKDAY_HEADER_HEIGHT,
                txt = print_day,
                align = 'C',
                border = border_flag,
                ln = 0,
                fill = fill_flag
            )

        # Move cursor down after weekday header
        self.set_y(self.get_y() + self.WEEKDAY_HEADER_HEIGHT)


    def _build_week(self, week_no: int):
        '''
        Build a week as seven columns of three row
        @param week_no: (int) week of month
        '''

        week_of_month = self.grid_days[week_no]

        cur_x = -1
        cur_y = -1

        week_cur_y = self.get_y()  # y position for current week and day-row element

        for d in range(self.DAYS):

            # Get month, day and meal information to be displayed
            month, day_of_month = week_of_month[d].split(':')
            meal = self._get_meal_for_day(month, day_of_month)

            if meal is not None and week_no in self.weeks_to_print:
                recipe = meal['recipe_name']
                cookbook_abbr = meal['abbr'] if 'abbr' in meal and meal['abbr'] != 'Unk' else ''
                meal_notes = meal['notes'] if 'notes' in meal else ''
                page = f'p.{meal["page"]}' if 'page' in meal and meal['page'] != 0 else ''
            else:
                recipe = ''
                cookbook_abbr = ''
                meal_notes = ''
                page = ''

            ln = 1 if d == self.DAYS - 1 else 0

            # Calculate the top-left corner of the cell
            x = self.margin_x + (d * self.DAY_CELL_WIDTH)
            y = self.DAY_CELL_START_Y + (week_no * self.DAY_CELL_HEIGHT)

            # if *not* printing only meals, draw rectangle
            if not self.only_meals:
                self.rect(x=x, y=y, w=self.DAY_CELL_WIDTH, h=self.DAY_CELL_HEIGHT)

            # Set the cursor position for the content
            self.set_xy(x + 0.05, y + 0.05)
          
            # Each calendar day is made of four sections/rows
            # r=0: (month abbreviation) day of month
            # r=1: recipe name
            # r=2: meal notes (if any)
            # r=3: cookbook and page
            # Process each section below

            # Add the day number
            self._print_calendar_day(day_of_month, month)

            # Add Recipe name
            self.set_xy(self.get_x(), self.get_y() +  0.1)  # put a little space between day and recipe
            r_start_x = self.get_x()
            self._print_recipe_name(recipe)

            # Add meal notes (if any)
            if len(meal_notes) > 0:
                self.set_xy(r_start_x, self.get_y() + 0.01)  # put a little space between recipe and notes
                self._print_meal_notes(y, self.get_x(), self.get_y(), meal_notes)
            
            # Add cookbook and page no
            c_bottom_y = y + self.DAY_CELL_HEIGHT
            self._print_cookbook(c_bottom_y, x, cookbook_abbr, page)


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


    def _print_calendar_day(self, day_of_month: int, month: int):
        '''
        Output the day of month
        @param day_of_month: day of month as integer
        @param month: month of year as integer   
        '''

        day_font = self.FONTS.day
        self.set_font(
            day_font.family,
            day_font.style,
            day_font.size
        )
        self.set_text_color(17, 120, 125)
        # month abbr if not current month
        if not self.only_meals:
            month_label = '' if int(month) == self.month else calendar.month_abbr[int(month)]
        else:
            month_label = ''
        line_start_x = self.get_x()            
        self.cell(
            self.DAY_CELL_WIDTH,
            0.1,
            txt = month_label,
            align = 'L',
            ln=0
        )
        # day of month
        day_label = '' if self.only_meals else f'{day_of_month}  ' # right padded with spaces
        self.set_x(line_start_x)
        self.cell(
            self.DAY_CELL_WIDTH,
            0.1,
            txt = day_label,
            align = 'R',
            ln=2
        )


    def _print_recipe_name(self, recipe_name: str):
        '''
        Outputs a recipe to calendar, wrapping text if required
        @param x: curent abscissa location
        @param y: current ordinate location
        @param recipe_name: name of recipe to print
        @param ln: line wrapping flag, 0 for stay on this line, 1 for next line
        @param c_border: border style
        '''

        recipe_font = self.FONTS.recipe        
        self.set_font(
            recipe_font.family,
            recipe_font.style,
            recipe_font.size
        )

        self.set_text_color(0, 0, 0)

        self.multi_cell(
            self.DAY_CELL_WIDTH - 0.1,
            0.15,
            recipe_name,
            0,
            'L'
        )


    def _print_meal_notes(self, cell_top: float, x: float, y: float, meal_notes: str):
        '''
        Output meal notes, wrapping text if required
        @param cell_top: ordinate value of cell top
        @param x: curent abscissa location
        @param y: current ordinate location
        @param meal_notes: name of recipe to print        
        '''

        cookbook_font = self.FONTS.cookbook
        notes_font = self.FONTS.notes         
        self.set_font(
            notes_font.family, 
            notes_font.style, 
            notes_font.size
        )

        fsize = notes_font.line_height

        # Determine if number of rows of meal notes need to be truncated
        # based on available space to print. Adjust font size by factor of 1.25
        used_space = y - cell_top
        max_lines = self._get_max_lines(self.DAY_CELL_HEIGHT, used_space, cookbook_font.size, notes_font.size)
        lines = self.multi_cell(w=self.DAY_CELL_WIDTH, h=fsize, txt=meal_notes, split_only=True)

        if len(lines) > max_lines:
            display_text = "\n".join(lines[:max_lines-1]) + "\n" + lines[max_lines-1][:-3] + "..."
        else:
            display_text = "\n".join(lines)
    
        self.multi_cell(
            self.DAY_CELL_WIDTH,
            fsize,
            display_text,
            0,
            'L'
        )


    def _print_cookbook(self, cell_bottom: float, start_x: float, cookbook_abbr: str, page: str):
        '''
        Output cookbook information
        @param cell_top: ordinate value of cell top
        @param cookbook_abbr: abbreviation of cookbook title
        @param page: page number of recipe
        '''
        
        # hack
        #if cell_bottom > self.HEIGHT - self.margin_y:
        #    cell_bottom = self.HEIGHT - self.margin_y - 0.5

        cookbook_font = self.FONTS.cookbook
        self.set_font(
            cookbook_font.family,
            cookbook_font.style,
            cookbook_font.size
        )
        self.set_text_color(33, 130, 63)

        fsize = cookbook_font.line_height
        start_y = cell_bottom - fsize
        self.set_xy(start_x, start_y)
        
        # print the cookbook abbreviation
        self.cell(
            self.DAY_CELL_WIDTH,
            fsize,
            txt=cookbook_abbr,
            align='L',
            ln=0
        )

        # print the page number 
        self.set_x(start_x)
        self.cell(
            self.DAY_CELL_WIDTH,
            fsize,
            txt = f'{page}',
            align = 'R',
            ln=0
        )


    def _get_next_month(self, month: int) -> tuple:
        '''
        Determines next month from specified month and year it occurs
        
        @param month: integer from 1-12 for month
        @returns: tuple next month as an integer 1 - 12 and year 
        '''

        next_month_int = month + 1
        next_month_yr = self.year
        if next_month_int == 13:
            next_month_int = 1
            next_month_yr = self.year + 1

        return (next_month_int, next_month_yr)
    
    
    def _get_previous_month(self, month: int) -> tuple:
        '''
        Determines previous month from specified month and year it occurs
        
        @param month: integer from 1-12 for month
        @returns: tuple next month as an integer 1 - 12 and year 
        '''

        prev_month_int = month - 1
        prev_month_yr = self.year
        if prev_month_int == 0:
            prev_month_int = 12
            prev_month_yr = self.year - 1

        return (prev_month_int, prev_month_yr)


    @staticmethod
    def _get_max_lines(total_box_h, used_h, reserved_font_size, content_font_size):
        '''
        Get maximum number of lines supported for multi cell given constraints
        
        :param total_box_h: total height of grid cell
        :param used_h: height already used in cell
        :param reserved_font_size: size of font for reserved section after multi cell
        :param content_font_size: size of font for content section (multi cell)
        '''
        # Calculate how much vertical space the reserved font needs (in inches)
        reserved_h = (reserved_font_size / 72) * 1.2

        # Calculate acutal content height based on font
        content_line_h = (content_font_size / 72) * 1.2

        # Calculate remaining space for the multi_cell
        available_h = total_box_h - used_h - reserved_h
        
        # Return the floor integer (you can't print half a line)
        return int(available_h // content_line_h)
