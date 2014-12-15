#!/usr/bin/env python

from financial_history import get_historical_records
from financial_future import get_future_projections_based_on
from financial_csv import write_to_csv_the

def main():
    historical_records = get_historical_records()
    future_projections = get_future_projections_based_on( historical_records )
    write_to_csv_the( financial_records = historical_records + future_projections )

# should it always just call main()
if __name__ == "__main__":
    main()
