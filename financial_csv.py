import csv

import financial_common

def write_to_csv_the(financial_records):
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

    with open('foobar.csv', 'wb') as csvfile:
        writer = csv.DictWriter(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, fieldnames=fieldnames)

        writer.writeheader()
        for finances_for_a_month in financial_records:
            writer.writerow(finances_for_a_month)
