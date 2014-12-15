from datetime import datetime
from dateutil.relativedelta import relativedelta

DATE = 'Date'
ASSETS = 'Assets'
LIABILITIES = 'Liabilities'
CAPITAL = 'Capital'
DUES = 'Dues'
DONATIONS = 'Donations'
FOOD_DONATIONS =  'Food donations'
MEMBERS = 'Members'
DONATING_MEMBERS = 'Donating members'
EXPENSES = 'Expenses'
FOOD_EXPENSES = 'Food expenses'
PROJECTED_CAPITAL = 'Projected capital'
PROJECTED_DUES = 'Projected dues'
PROJECTED_DONATIONS = 'Projected donations'
PROJECTED_MEMBERS = 'Projected members'
PROJECTED_DONATING_MEMBERS = 'Projected donating members'
PROJECTED_FOOD_DONATIONS = 'Projected food donations'
PROJECTED_FOOD_EXPENSES = 'Projected food expenses'
CAPITAL_TARGET = 'Target balance (3 month buffer)'

MONTH_START_DAY = 4

def figure_out_today_and_start_and_end_dates():
    today = datetime.now().replace(second=0, microsecond=0)
    if today.day < MONTH_START_DAY:
        today -= relativedelta(months=+1)
    delta = relativedelta(months=+6)
    start = today - delta
    end = today + delta

    return [start, today, end]

def report_days(start_date, end_date):
    delta = relativedelta(months=+1)
    d = start_date.replace(day=MONTH_START_DAY)
    while d < end_date.replace(day=MONTH_START_DAY):
        d += delta
        yield d
