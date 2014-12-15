import calendar
import gnucashxml
import sys
from datetime import datetime
from __future__ import print_function

import financial_common

def get_historical_records():
    historical_records = []

    book = get_requested_financial_book()

    for month in months_to_report_on():
        historical_records.append( book.finances_for( month ) )

    return historical_records

def get_requested_financial_book():
    provided_by_user = sys.argv[1]
    return Book( gnucash_filename = provided_by_user )

def months_to_report_on():
    start, today, end = figure_out_today_and_start_and_end_dates()
    return report_days( start, today )

class Book:
    def __init__( self, gnucash_filename ):
        self.book = gnucashxml.from_filename( gnucash_filename )

    def finances_for( self, month, book ):
        assets = self.get_assets_on( date = month )
        liabilities = self.get_liability_on( date = month )
        expenses = self.get_expenses_for( month )

        monthly_finances = {
            DATE: month,
            ASSETS: assets,
            LIABILITIES: liabilities,
            CAPITAL: assets + liabilities,
            DUES: self.get_amount_of( "Member Dues", month ),
            DONATIONS: self.get_amount_of( "Regular donations", month ),
            FOOD_DONATIONS: self.get_amount_of( "Food and Drink Donations", month ),
            MEMBERS: self.get_number_of( "Member Dues", month ),
            DONATING_MEMBERS: self.get_number_of( "Regular donations", month ),
            EXPENSES: expenses,
            FOOD_EXPENSES: self.get_amount_of( "Groceries", month ),
            CAPITAL_TARGET: expenses * -3,
        }

        display( monthly_finances )

        return monthly_finances

    def get_assets_on( self, date ):
        assets = self.book.find_account("Current Assets")

        asset_total = 0
        for account in assets.children:
            if account.name != "Prepaid Rent":
                asset_total += sum(split.value for split in account.splits if split.transaction.date.replace(tzinfo=None) <= date)

        return asset_total

    def get_liability_on( self, date ):
        liability = self.get_total( "Active Members", date ) + self.get_total( "Former Members", date )

        return liability

    def get_total( self, account_name, date ):
        account = self.book.find_account( account_name )
        total = sum( split.value for split in account.get_all_splits() if split.transaction.date.replace(tzinfo=None) <= date)

        return total

    def get_expenses_for( self, month_end ):
        end_date = month_end
        start_date = subtract_month(month_end)

        expense_accounts = self.book.find_account("Expenses")
        expenses = 0
        for account in expense_accounts.children:
            if account.name != "Anti-social 10-04" and account.name != "Groceries":
                for split in account.splits:
                    if start_date < split.transaction.date.replace(tzinfo=None) <= end_date:
                        expenses += split.value

                for subaccount in account.children:
                    for split in subaccount.splits:
                        if start_date < split.transaction.date.replace(tzinfo=None) <= end_date:
                            expenses += split.value


        return expenses * -1

    def get_number_of( self, account_name, month_end ):
        return sum( len( entry.transaction.splits ) - 1 for entry in self.get_entries_for( account_name, month_end ) )

    def get_amount_of( self, account_name, month_end ):
        return sum( entry.value for entry in self.get_entries_for( account_name, month_end ) ) * -1

    def get_entries_for( self, account_name, month_end ):
        end_date = month_end
        start_date = subtract_month(month_end)

        account = self.book.find_account( account_name )

        entries = []

        for split in account.get_all_splits():
            if start_date < split.transaction.date.replace(tzinfo=None) <= end_date:
                entries.add( split )

        return entries

def subtract_month(date):
    month = date.month - 2
    month = month % 12 + 1
    year = date.year - 1/12
    day = min(date.day, calendar.monthrange(year, month)[1])
    return datetime(year, month, day)

def display( monthly_finances ):
    print(monthly_finances[ DATE ])
    print("Total assets: ", monthly_finances[ ASSETS ])
    print("Total liability: ", monthly_finances[ LIABILITIES ])
    print("Available capital: ", monthly_finances[ CAPITAL ])
    print("Dues collected last month: ", monthly_finances[ DUES ])
    print("Dues paying members: ", monthly_finances[ MEMBERS ])
    print("Regular donations collected last month: ", monthly_finances[ DONATIONS ])
    print("Regularly donating members: ", monthly_finances[ DONATING_MEMBERS ])
    print("Food donations: ", monthly_finances[ FOOD_DONATIONS ])
    print("Total expected income: ", (monthly_finances[ DUES ] + monthly_finances[ DONATIONS ] + monthly_finances[ FOOD_DONATIONS ]))
    print("Expenses: ", monthly_finances[ EXPENSES ])
    print("Food expenses: ", monthly_finances[ FOOD_EXPENSES ])
    print()
