import requests 
import datetime
import os
from bokeh.plotting import figure 
from bokeh.io import output, output_file, show

###########################################################
# EXAMPLE: Data retrieval format
###########################################################

# response = requests.get("https://api.fitbit.com/1/user/-/activities/log/steps/date/2019-01-01/today.json", headers=header).json()


###########################################################
# StepDiary Class
###########################################################

class StepDiary :
    
    #   Class variables
    date_str_format = "%Y-%m-%d"
    week_dict = { 1 : "Mon", 2 : "Tue", 3 : "Wed", 4 : "Thu", 5 : "Fri", 6 : "Sat", 7 : "Sun" }

    #   Init method
    def __init__ (self, access_token, prefix_url = "https://api.fitbit.com/1/user/-/", suffix_url = ".json") :
        self._access_token = access_token
        self._prefix_url = prefix_url
        self._suffix_url = suffix_url
        self._header = { "Authorization" : f"Bearer {self._access_token}" }

    #   Making access token, prefix url, suffix url and header read only
    @property
    def access_token (self) :
        return self._access_token

    @property
    def prefix_url (self) :
        return self._prefix_url

    @property
    def suffix_url (self) :
        return self._suffix_url

    @property
    def header (self) :
        return self._header

    #   Retrieve lifetime steps
    @property
    def lifetime (self):
        '''Returns the total number of steps since the user became a member of Fitbit.'''
        url = self.prefix_url + "activities" + self.suffix_url
        response = requests.get(url, headers=self.header).json()

        lifetime_steps = response["lifetime"]["tracker"]["steps"]

        return int(lifetime_steps)

    #   Retrieve the user's total steps for the current day
    @property
    def current_day (self) :
        '''Retrieve the user's total number of steps for the current day (up to most recent sync).'''

        #   Datetime and string objects for today's date
        tday = datetime.datetime.today()
        tday_str = tday.strftime(self.date_str_format)

        #   Retrieve required data from fitbit
        url = self.prefix_url + f"activities/date/{tday_str}" + self.suffix_url
        response = requests.get(url, headers=self.header).json()

        #   Extract required output
        output = response['summary']['steps']

        return output

    #   Retrieve the user's total steps for the current week
    @property
    def current_week (self) :
        '''Retrieve the user's total number of steps for the current week (up to most recent sync).'''

        #   Datetime and string objects for today's date
        tday = datetime.datetime.today()
        tday_str = tday.strftime(self.date_str_format)

        #   Datetime and string objects for start of current week
        sow = self.week_of(tday)[0]
        sow_str = sow.strftime(self.date_str_format)

        #   Retrieve required data from fitbit
        url = self.prefix_url + f"activities/log/steps/date/{sow_str}/{tday_str}" + self.suffix_url
        response = requests.get(url, headers=self.header).json()

        #   Extract steps from the messy dictionary that response is
        messy_dict = list(response.values())[0]

        #   Sum the steps to obtain the output
        total = 0
        for entry in messy_dict:
            total += int(entry['value'])

        return total

    #   Retrieve the user's total steps for the current month
    @property
    def current_month (self) :
        '''Retrieve the user's total number of steps for the current month (up to most recent sync).'''

        #   Datetime and string objects for today's date
        tday = datetime.datetime.today()
        tday_str = tday.strftime(self.date_str_format)

        #   Datetime and string objects for start of current month
        som = self.month_of(tday)[0]
        som_str = som.strftime(self.date_str_format)

        #   Retrieve required data from fitbit
        url = self.prefix_url + f"activities/log/steps/date/{som_str}/{tday_str}" + self.suffix_url
        response = requests.get(url, headers=self.header).json()

        #   Extract steps from the messy dictionary that response is
        messy_dict = list(response.values())[0]

        #   Sum the steps to obtain the output
        total = 0
        for entry in messy_dict:
            total += int(entry['value'])

        return total
    
    #   Retrieve the user's total steps for the current year
    @property
    def current_year (self) :
        '''Retrieve the user's total number of steps for the current year (up to most recent sync).'''

        #   Datetime and string objects for today's date
        tday = datetime.datetime.today()
        tday_str = tday.strftime(self.date_str_format)

        #   Datetime and string objects for start of current year
        soy = self.year_of(tday)[0]
        soy_str = soy.strftime(self.date_str_format)  

        #   Retrieve required data from fitbit
        url = self.prefix_url + f"activities/log/steps/date/{soy_str}/{tday_str}" + self.suffix_url
        response = requests.get(url, headers=self.header).json()

        #   Extract steps from the messy dictionary that response is
        messy_dict = list(response.values())[0]

        #   Sum the steps to obtain the output
        total = 0
        for entry in messy_dict:
            total += int(entry['value'])

        return total


    #   Method to print a summary (current day, current week, current month, current year and lifetime) to the console
    @property
    def summary (self) :
        '''Print to the console a summary of the user's steps for the current day, week, month and year, and their lifetime steps.'''

        #   Store summary stats as a dictionary
        summary = dict()

        summary["Today: "] = self.current_day
        summary["This week: "] = self.current_week
        summary["This month: "] = self.current_month
        summary["This year: "] = self.current_year
        summary["\nLifetime: "] = self.lifetime # little trick to force spacing when printing with for loop

        #   Format steps with thousand comma-separation
        for key, val in summary.items():
            summary[key] = "{:,}".format(val)

        #   Print summary statistics
        print("\nYour summary statistics (total steps)", "\n")

        for key, val in summary.items():
            print(key, val)

        #   Produce plots
        self.current_week_plot()
        self.current_month_plot()
        self.current_year_plot()

    #   Retrieve total steps for the last N days
    def lastNdays (self, N:int) :
        '''Return the user's total number of steps for the last N days'''

        #   Get todays date
        tday = datetime.datetime.combine(datetime.date.today(), datetime.time(23))

        #   Convert N days into seconds
        N_secs = datetime.timedelta(days=(N-1)) # not including the end date as we include today!

        #   Find first date to count from
        start_date = tday - N_secs
        start_date = start_date.date()

        #   Get strings of tday and start_date
        start_str = start_date.strftime(self.date_str_format)
        tday_str = tday.strftime(self.date_str_format)

        #   Retrieve required data from fitbit
        url = self.prefix_url + f"activities/log/steps/date/{start_str}/{tday_str}" + self.suffix_url
        response = requests.get(url, headers=self.header).json()

        #   Extract steps from the messy dictionary that response is
        messy_dict = list(response.values())[0]

        #   Sum the steps to obtain the output
        total = 0
        for entry in messy_dict:
            total += int(entry['value'])

        return total

    #   Retrieve total steps for last 7 days
    def last7days (self) :
        '''Retrieve the user's total steps for the last 7 days.'''
        return self.lastNdays(7)

    #   Retrieve total steps for last 28 days
    def last28days (self) :
        '''Retrieve the user's total steps for the last 28 days.'''
        return self.lastNdays(28)

    #   Calculate the average steps (rounded down to the nearest integer) for the last N days
    def lastNdays_avg (self, N:int) :
        '''Calculate the user's average daily steps (rounded DOWN to nearest integer) for the last N days.'''
        return self.lastNdays(N) // N

    #   Calculate the averages steps (rounded down to the nearest integer) for the last 7 days
    def last7days_avg (self) :
        return self.lastNdays_avg(7)

    #   Calculate the averages steps (rounded down to the nearest integer) for the last 28 days
    def last28days_avg (self) :
        return self.lastNdays_avg(28)

    #   Class method for ensuring dates are a datetime object
    @classmethod
    def process_date(cls, date) :
        '''Takes a date as a str "YYYY-MM-DD", or as a datetime object, without time component and returns the corresponding datetime object with time component (in ISO format).'''
        if isinstance(date, str):
            date = datetime.datetime.strptime(date, cls.date_str_format)
        elif isinstance(date, datetime.date):
            date = datetime.datetime.combine(date, datetime.time(00))

        return date

    #   Class method for finding the start and end of the week for a given date.
    @classmethod
    def week_of (cls, date) :
        '''Takes a date as a str YYYY-MM-DD, or a datetime object, and returns a tuple (sow, eow) with datetime objects for the start and end of the week that date belongs to (Mon-Sun).'''

        #   Ensure date is an instance of datetime.date (correct format we need for isoweekday)
        date = cls.process_date(date)
        
        #   Retrieve the day of the week for this date. Returns a number 1-7 (see week_dict), ...
        day = date.isoweekday()

        #   Identify how many dates before and after this date we need to consider
        before, after = day - 1, 7 - day
        
        #   Convert these differences from days (ints) into seconds (timedelta objects)
        before_secs = datetime.timedelta(days=before)
        after_secs = datetime.timedelta(days=after)

        #   Calculate the date for start of week and date for end of week as datetime objects
        sow = (date - before_secs).date()
        eow = (date + after_secs).date()

        return sow, eow

    #   Class method for finding the start and end dates of the month of a given date.
    @classmethod
    def month_of (cls, date) :
        '''Takes a date as a str YYYY-MM-DD, or a datetime object, and returns a tuple (som, eom) with datetime objects for the start and end of the month that date belongs to (calendar month).'''

        #   Ensure date is in required format.
        date = cls.process_date(date)

        #   Store current mnth as an 2 character string 01-12. 
        if date.month < 10 :
            mnth_str = "0"+ str(date.month)
        else:
            mnth_str = str(date.month)
        
        #   Store the year as a 4 character string - should never be less than or more than 4 characters!
        yr_str = str(date.year)

        #   Construct first day of the month
        som_str = yr_str + "-" + mnth_str + "-" + "01"
        som = datetime.datetime.strptime(som_str, cls.date_str_format)
        
        #   Construct last day of the month (which is different for different length months)
        nxt_mnth_month = date.month + 1
        
        if nxt_mnth_month == 13:
            nxt_mnth_month = 1
            nxt_mnth_year = str(date.year + 1)
        else:
            nxt_mnth_year = str(date.year)
        
        if nxt_mnth_month < 10 :
            nxt_mnth_month = "0"+ str(nxt_mnth_month)
        else:
            nxt_mnth_month = str(nxt_mnth_month)
        
        sonm_str = nxt_mnth_year + "-" + nxt_mnth_month + "-" + "01" # date string for start of next month
        sonm = datetime.datetime.strptime(sonm_str, cls.date_str_format)

        eom = sonm - datetime.timedelta(seconds=1)
        eom = datetime.datetime.combine(eom, datetime.time(00))

        #   Ignore time
        eom, som = eom.date(), som.date()

        return som, eom

    #   Class method for finding the start and end dates of the year of a given date
    @classmethod
    def year_of (cls, date) :
        '''Takes a date as a str YYYY-MM-DD, or a datetime object, and returns a tuple (soy, eoy) with datetime objects for the start and end of the year that date belongs to (calendar year).'''

        #   Ensure date is in required format.
        date = cls.process_date(date)

        #   Store the yr
        yr_str = str(date.year)

        #   Construct start of year (1st January)
        soy_str = yr_str + "-01-01"
        soy = datetime.datetime.strptime(soy_str, cls.date_str_format)

        #   Construct end of year (31st December)
        eoy_str = yr_str + "-12-31"
        eoy = datetime.datetime.strptime(eoy_str, cls.date_str_format)

        #   Ignore time
        soy, eoy = soy.date(), eoy.date()

        return soy, eoy

    ########################################################
    # GRAPH PLOTTING METHODS    #
    ########################################################

    #   Plot current year as a line graph
    def current_year_plot (self) :

        #   Datetime and string objects for today's date
        tday = datetime.datetime.today()
        tday_str = tday.strftime(self.date_str_format)

        #   Datetime and string objects for start of current year
        soy = self.year_of(tday)[0]
        soy_str = soy.strftime(self.date_str_format)  

        #   Retrieve required data from fitbit
        url = self.prefix_url + f"activities/log/steps/date/{soy_str}/{tday_str}" + self.suffix_url
        response = requests.get(url, headers=self.header).json()

        #   Extract steps from the messy dictionary that response is
        messy_dict = list(response.values())[0]

        #   Extract dates and steps as tuples
        tples = []
        for item in messy_dict:
            tples.append((self.process_date(item["dateTime"]), int(item["value"])))

        # store data
        x = list()
        y = list()

        for item in tples:
            x.append(item[0])
            y.append(item[1])

        # output file
        output_file("graphs/currentyear.html")

        #   Create a plot
        f = figure(x_axis_type="datetime", plot_width=1000, plot_height=500) 
        f.title.text = "Current Year"

        # line graph
        f.line(x, y)

        # Show graph
        # show(f)


    #   Plot current month as a line graph
    def current_month_plot (self) :
        
        #   Datetime and string objects for today's date
        tday = datetime.datetime.today()
        tday_str = tday.strftime(self.date_str_format)

        #   Datetime and string objects for start of current month
        som = self.month_of(tday)[0]
        som_str = som.strftime(self.date_str_format)

        #   Retrieve required data from fitbit
        url = self.prefix_url + f"activities/log/steps/date/{som_str}/{tday_str}" + self.suffix_url
        response = requests.get(url, headers=self.header).json()

        #   Extract steps from the messy dictionary that response is
        messy_dict = list(response.values())[0]

        #   Extract dates and steps as tuples
        tples = []
        for item in messy_dict:
            tples.append((self.process_date(item["dateTime"]), int(item["value"])))

        # store data
        x = list()
        y = list()

        for item in tples:
            x.append(item[0])
            y.append(item[1])

        # output file
        output_file("graphs/currentmonth.html")

        #   Create a plot
        f = figure(x_axis_type="datetime", plot_width=1000, plot_height=500)   
        f.title.text = "Current Month"

        # line graph
        f.line(x, y)

        # Show graph
        # show(f)


    #   Plot current week as a line graph
    def current_week_plot (self) :

        #   Datetime and string objects for today's date
        tday = datetime.datetime.today()
        tday_str = tday.strftime(self.date_str_format)

        #   Datetime and string objects for start of current week
        sow = self.week_of(tday)[0]
        sow_str = sow.strftime(self.date_str_format)

        #   Retrieve required data from fitbit
        url = self.prefix_url + f"activities/log/steps/date/{sow_str}/{tday_str}" + self.suffix_url
        response = requests.get(url, headers=self.header).json()

        #   Extract steps from the messy dictionary that response is
        messy_dict = list(response.values())[0]

        #   Extract dates and steps as tuples
        tples = []
        for item in messy_dict:
            tples.append((self.process_date(item["dateTime"]), int(item["value"])))

        # store data
        x = list()
        y = list()

        for item in tples:
            x.append(item[0])
            y.append(item[1])

        # output file
        output_file("graphs/currentweek.html")

        #   Create a plot
        f = figure(x_axis_type="datetime", plot_width=1000, plot_height=500)  
        f.title.text = "Current Week"

        # line graph
        f.line(x, y)

        # Show graph
        # show(f)



###########################################################
# STEP DIARY OBJECT INSTANTIATION
###########################################################
token = os.environ.get("fitbit_access_token")
jamie = StepDiary(token)  

###########################################################
# TESTING
###########################################################

jamie.summary




