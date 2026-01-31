from fpdf import FPDF
from datetime import datetime, timedelta

class CalendarPDF(FPDF):
    """
    A class to create a landscape PDF document with a 7x5 grid.
    This class inherits from FPDF and adds methods for drawing the grid.
    """

    def __init__(self, orientation='L', unit='in', format='Letter'):
        """
        Initializes the CalendarPDF object.
        Calls the parent class constructor to set up the PDF in landscape format.
        """
        super().__init__(orientation, unit, format)
        self.data = {}
        self.month = None
        self.year = None

    def set_calendar_data(self, month, year, data):
        """
        Sets the month, year, and recipe data for the calendar.

        Args:
            month (int): The month number (1-12).
            year (int): The year.
            data (dict): A dictionary where keys are tuples (month, day, year)
                         and values are dictionaries with recipe information.
        """
        self.month = month
        self.year = year
        self.data = data

    def draw_grid_with_data(self):
        """
        Draws the 7x5 calendar grid with a title, day headers, and recipe information.
        """
        # --- DIMENSION CONSTANTS ---
        title_height = 0.5
        header_height = 0.3
        margin_x = 0.5
        margin_y = 0.5
        
        # --- TITLE ---
        # Set the font for the title
        self.set_font('Helvetica', 'B', 18)
        # Set the title text color to blue (RGB)
        self.set_text_color(0, 0, 255)
        # Create the title string
        month_name = datetime(self.year, self.month, 1).strftime('%B %Y')
        title_text = f"Meal Plan - {month_name}"
        # Draw the title on the page
        self.cell(0, title_height, title_text, 0, 1, 'C')
        # Reset the text color to black for the rest of the content
        self.set_text_color(0, 0, 0)

        # --- DAY OF THE WEEK HEADERS ---
        # Set the font for the header row
        self.set_font('Helvetica', 'B', 14)
        # Set the fill color for the header row background to beige (RGB)
        self.set_fill_color(245, 245, 220)
        
        days_of_week = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        for i, day in enumerate(days_of_week):
            self.set_xy(margin_x + i * (self.w - 2 * margin_x) / 7, self.get_y())
            # Draw a filled cell with a border for the header
            self.cell((self.w - 2 * margin_x) / 7, header_height, day, 1, 0, 'C', True)
        
        self.set_y(self.get_y() + header_height) # Move cursor down after the header row

        # --- GRID DIMENSIONS ---
        # FIX: Re-calculate the usable height to account for the title and header.
        # This prevents the last row from being cut off.
        usable_height = self.h - (2 * margin_y) - title_height - header_height

        cell_width = (self.w - 2 * margin_x) / 7
        cell_height = usable_height / 5

        # Find the starting date for the calendar grid
        first_day = datetime(self.year, self.month, 1)
        # datetime.weekday() returns Monday as 0. We'll start our grid on Sunday.
        start_day_offset = (first_day.weekday() + 1) % 7
        start_date = first_day - timedelta(days=start_day_offset)

        # Set line styles for the grid
        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.01)

        current_date = start_date
        start_y_grid = self.get_y()

        for row in range(5):
            for col in range(7):
                # Calculate the top-left corner of the cell
                x = margin_x + (col * cell_width)
                y = start_y_grid + (row * cell_height)

                # Draw the cell rectangle
                self.rect(x=x, y=y, w=cell_width, h=cell_height)

                # Set the cursor position for the content
                self.set_xy(x + 0.05, y + 0.05)
                
                # Add the day number
                self.set_font('Helvetica', 'B', 10)
                self.cell(cell_width, 0.1, str(current_date.day), ln=2)

                # Check if this date has a recipe
                date_key = (current_date.month, current_date.day, current_date.year)
                if date_key in self.data:
                    recipe_info = self.data[date_key]
                    self.set_font('Helvetica', '', 8)
                    # Use multi_cell for multi-line text
                    self.multi_cell(
                        cell_width - 0.1, 
                        0.15,
                        f"Recipe: {recipe_info['recipe_name']}\nCookbook: {recipe_info['cookbook']}\nPage: {recipe_info['page_number']}",
                        0, 'L'
                    )

                # Move to the next day
                current_date += timedelta(days=1)

    def create_pdf(self, month, year, filename="calendar_grid.pdf", data=None):
        """
        Creates and saves the PDF document with the calendar grid and data.

        Args:
            month (int): The month number (1-12).
            year (int): The year.
            filename (str): The name of the output PDF file.
            data (dict, optional): A dictionary of recipes. Defaults to an empty dictionary.
        """
        if data is None:
            data = {}
        self.set_calendar_data(month, year, data)
        self.add_page()
        self.draw_grid_with_data()
        self.output(filename)
        print(f"Successfully created '{filename}'")

if __name__ == "__main__":
    # Sample data for a recipe calendar
    sample_recipes = {
        (10, 5, 2025): {
            'recipe_name': 'Spicy Chicken Curry',
            'cookbook': 'World Flavors',
            'page_number': 45
        },
        (10, 15, 2025): {
            'recipe_name': 'Lentil Soup',
            'cookbook': 'Quick & Easy Meals',
            'page_number': 12
        },
        (10, 22, 2025): {
            'recipe_name': 'Beef Stroganoff',
            'cookbook': 'Classic Dishes',
            'page_number': 87
        }
    }
    
    # Create the PDF for October 2025 with the sample data
    calendar = CalendarPDF()
    calendar.create_pdf(
        month=10, 
        year=2025, 
        data=sample_recipes, 
        filename="October_2025_recipes.pdf"
    )
