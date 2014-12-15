from __future__ import print_function
from datetime import datetime

import financial_common

def get_future_projections_based_on( historical_records ):
    future_projections = []

    monthly_amount_projections = get_monthly_amount_projections_based_on( historical_records )

    for month in months_to_project():
        starting_capital = future_projections[-1][PROJECTED_CAPITAL] if len(future_projections) else historical_records[-1][CAPITAL]

        future_projections.append( project_finances_for( month, starting_capital, finances_for_current_month, monthly_amount_projections ) )

    return future_projections

def months_to_project():
    start, today, end = figure_out_today_and_start_and_end_dates()
    return report_days(today, end)

def project_finances_for( month, starting_capital, finances_for_current_month, monthly_amount_projections ):
    print(month)

    return {
        # same for each projected month
        DATE: month,
        PROJECTED_DUES: finances_for_current_month[DUES],
        PROJECTED_DONATIONS: finances_for_current_month[DONATIONS],
        PROJECTED_MEMBERS: finances_for_current_month[MEMBERS],
        PROJECTED_DONATING_MEMBERS: finances_for_current_month[DONATING_MEMBERS],
        PROJECTED_FOOD_DONATIONS: monthly_amount_projections[ 'food income' ],
        PROJECTED_FOOD_EXPENSES: monthly_amount_projections[ 'food expenses' ],

        # differs in each month
        PROJECTED_CAPITAL: starting_capital + monthly_amount_projections['income'] + monthly_amount_projections['expenses'],

        # two different values - before & after rent increase
        CAPITAL_TARGET: (monthly_amount_projections['expenses'] - rent_increase_for( month )) * -3,
    }

def get_monthly_amount_projections_based_on( historical_records ):
    current_month_amounts = historical_records[-1]

    monthly_amount_projections['income'] = current_month_amounts[DUES] + current_month_amounts[DONATIONS]
    monthly_amount_projections['expenses'] = get_average( EXPENSES, historical_records )
    monthly_amount_projections['food income'] = get_average( FOOD_DONATIONS, historical_records )
    monthly_amount_projections['food expenses'] = get_average( FOOD_EXPENSES, historical_records )

    print( "Projected income: ", monthly_amount_projections['income'] )
    print( "Projected expenses: ", monthly_amount_projections['expenses'] )

    return monthly_amount_projections

def rent_increase_for( month ):
    february_2015 = datetime(2015, 02, 01):

    if month >= february_2015
        rent_increase = 100
    else
        rent_increase = 0

    return rent_increase

def get_average( datum_key, financial_records ):
    total = sum( record[datum_key] for record in financial_records )

    return total / len( financial_records )
