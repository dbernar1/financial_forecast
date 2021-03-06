#!/usr/bin/env python

from __future__ import print_function
import sys
from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar
#import getpass
import gnucashxml
import csv


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


def main():
    filename = sys.argv[1]
    book = gnucashxml.from_filename(filename)

    today = datetime.now().replace(second=0, microsecond=0)
    if today.day < MONTH_START_DAY:
        today -= relativedelta(months=+1)
    delta = relativedelta(months=+6)
    start = today - delta
    end = today + delta

    history = []

    for month in report_days(start, today):
        print(month)
        assets = get_assets_on_date(book, month)
        liabilities = get_liability_on_date(book, month)
        capital = assets + liabilities
        dues = get_dues_for_month(book, month)
        donations = get_donations_for_month(book, month)
        food_donations = get_food_donations_for_month(book, month)
        members = get_paying_members(book, month)
        donating_members = get_donating_members(book, month)
        expenses = get_expenses_for_month(book, month)
        food_expenses = get_food_expenses_for_month(book, month)

        print("Total assets: ", assets)
        print("Total liability: ", liabilities)
        print("Available capital: ", capital)
        print("Dues collected last month: ", dues)
        print("Dues paying members: ", members)
        print("Regular donations collected last month: ", donations)
        print("Regularly donating members: ", donating_members)
        print("Food donations: ", food_donations)
        print("Total expected income: ", (dues + donations + food_donations))
        print("Expenses: ", expenses)
        print("Food expenses: ", food_expenses)

        history.append({
            DATE: month,
            ASSETS: assets,
            LIABILITIES: liabilities,
            CAPITAL: capital,
            DUES: dues,
            DONATIONS: donations,
            FOOD_DONATIONS: food_donations,
            MEMBERS: members,
            DONATING_MEMBERS: donating_members,
            EXPENSES: expenses,
            FOOD_EXPENSES: food_expenses,
            CAPITAL_TARGET: expenses * -3,
        })

        print()

    income = get_projected_income(history)
    expenses = get_projected_expenses(history)
    print("Projected income: ", income)
    print("Projected expenses: ", expenses)

    food_income = get_projected_food_income(history)
    food_expenses = get_projected_food_expenses(history)

    history[-1][PROJECTED_CAPITAL] = history[-1][CAPITAL]
    history[-1][PROJECTED_DUES] = history[-1][DUES]
    history[-1][PROJECTED_DONATIONS] = history[-1][DONATIONS]
    history[-1][PROJECTED_MEMBERS] = history[-1][MEMBERS]
    history[-1][PROJECTED_DONATING_MEMBERS] = history[-1][DONATING_MEMBERS]
    #history[-1][PROJECTED_FOOD_DONATIONS] = history[-1][FOOD_DONATIONS]
    #history[-1][PROJECTED_FOOD_EXPENSES] = history[-1][FOOD_EXPENSES]


    for month in report_days(today, end):
        print(month)

        rent_increase = 0
        if month >= datetime(2015, 02, 01):
            rent_increase = -100

        history.append({
            DATE: month,
            PROJECTED_CAPITAL: history[-1][PROJECTED_CAPITAL] + income + expenses,
            PROJECTED_DUES: history[-1][PROJECTED_DUES],
            PROJECTED_DONATIONS: history[-1][PROJECTED_DONATIONS],
            PROJECTED_MEMBERS: history[-1][PROJECTED_MEMBERS],
            PROJECTED_DONATING_MEMBERS: history[-1][PROJECTED_DONATING_MEMBERS],
            PROJECTED_FOOD_DONATIONS: food_income,
            PROJECTED_FOOD_EXPENSES: food_expenses,
            CAPITAL_TARGET: (expenses + rent_increase) * -3,
        })

    with open('foobar.csv', 'wb') as csvfile:
        fieldnames = [
            DATE,
            ASSETS,
            LIABILITIES,
            CAPITAL,
            PROJECTED_CAPITAL,
            DUES,
            PROJECTED_DUES,
            DONATIONS,
            PROJECTED_DONATIONS,
            MEMBERS,
            PROJECTED_MEMBERS,
            DONATING_MEMBERS,
            PROJECTED_DONATING_MEMBERS,
            EXPENSES,
            FOOD_DONATIONS,
            PROJECTED_FOOD_DONATIONS,
            FOOD_EXPENSES,
            PROJECTED_FOOD_EXPENSES,
            CAPITAL_TARGET,
        ]



        writer = csv.DictWriter(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, fieldnames=fieldnames)

        writer.writeheader()
        for history_item in history:
            writer.writerow(history_item)


def get_assets_on_date(book, date):
    assets = book.find_account("Current Assets")

    asset_total = 0
    for account in assets.children:
        if account.name != "Prepaid Rent":
            asset_total += sum(split.value for split in account.splits if split.transaction.date.replace(tzinfo=None) <= date)

    return asset_total


def get_liability_on_date(book, date):
    liabilities = book.find_account("Active Members")
    liability_total = sum(split.value for split in liabilities.get_all_splits() if split.transaction.date.replace(tzinfo=None) <= date)

    liabilities = book.find_account("Former Members")
    liability_total += sum(split.value for split in liabilities.get_all_splits() if split.transaction.date.replace(tzinfo=None) <= date)

    return liability_total


def get_dues_for_month(book, month_end):
    end_date = month_end
    start_date = subtract_month(month_end)

    member_dues = book.find_account("Member Dues")
    dues = 0
    for split in member_dues.get_all_splits():
        if start_date < split.transaction.date.replace(tzinfo=None) <= end_date:
            dues += split.value

    return dues * -1


def get_paying_members(book, month_end):
    end_date = month_end
    start_date = subtract_month(month_end)

    member_dues = book.find_account("Member Dues")
    members = 0
    for split in member_dues.get_all_splits():
        if start_date < split.transaction.date.replace(tzinfo=None) <= end_date:
            members += len(split.transaction.splits) - 1

    return members


def get_donations_for_month(book, month_end):
    end_date = month_end
    start_date = subtract_month(month_end)

    member_donations = book.find_account("Regular donations")
    donations = 0
    for split in member_donations.get_all_splits():
        if start_date < split.transaction.date.replace(tzinfo=None) <= end_date:
            donations += split.value

    return donations * -1


def get_expenses_for_month(book, month_end):
    end_date = month_end
    start_date = subtract_month(month_end)

    expense_accounts = book.find_account("Expenses")
    expenses = 0
    for account in expense_accounts.children:
        if account.name != "Anti-social 10-04" and account.name != "Groceries":
            #print(account.name)
            for split in account.splits:
                if start_date < split.transaction.date.replace(tzinfo=None) <= end_date:
                    expenses += split.value
                    #print("\t", split.transaction.description, " \t", split.value)

            for subaccount in account.children:
                #print("\t", subaccount.name)
                for split in subaccount.splits:
                    if start_date < split.transaction.date.replace(tzinfo=None) <= end_date:
                        expenses += split.value
                        #print("\t\t", split.transaction.description, " \t", split.value)


    return expenses * -1


def get_food_expenses_for_month(book, month_end):
    end_date = month_end
    start_date = subtract_month(month_end)

    expense_accounts = book.find_account("Groceries")
    expenses = 0
    for split in expense_accounts.get_all_splits():
        if start_date < split.transaction.date.replace(tzinfo=None) <= end_date:
            expenses += split.value
            #print("\t", split.transaction.description, " \t", split.value)

    return expenses * -1


def get_food_donations_for_month(book, month_end):
    end_date = month_end
    start_date = subtract_month(month_end)

    food_donations = book.find_account("Food and Drink Donations")
    donations = 0
    for split in food_donations.get_all_splits():
        if start_date < split.transaction.date.replace(tzinfo=None) <= end_date:
            donations += split.value

    return donations * -1


def get_donating_members(book, month_end):
    end_date = month_end
    start_date = subtract_month(month_end)

    member_dues = book.find_account("Regular donations")
    members = 0
    for split in member_dues.get_all_splits():
        if start_date < split.transaction.date.replace(tzinfo=None) <= end_date:
            members += len(split.transaction.splits) - 1

    return members


def subtract_month(date):
    month = date.month - 2
    month = month % 12 + 1
    year = date.year - 1/12
    day = min(date.day, calendar.monthrange(year, month)[1])
    return datetime(year, month, day)


def report_days(start_date, end_date):
    delta = relativedelta(months=+1)
    d = start_date.replace(day=MONTH_START_DAY)
    while d < end_date.replace(day=MONTH_START_DAY):
        d += delta
        yield d


def get_projected_income(history):
    return history[-1][DUES] + history[-1][DONATIONS]


def get_projected_expenses(history):
    expenses = 0
    for data_point in history:
        expenses += data_point[EXPENSES]

    return expenses / len(history)


def get_projected_food_income(history):
    income = 0
    for data_point in history:
        income += data_point[FOOD_DONATIONS]

    return income / len(history)


def get_projected_food_expenses(history):
    expenses = 0
    for data_point in history:
        expenses += data_point[FOOD_EXPENSES]

    return expenses / len(history)


if __name__ == "__main__":
    main()
