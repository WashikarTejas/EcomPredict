"""
Data Quality Validation Module for E-Commerce Sales Intelligence.
Detects missing values, duplicates, invalid discounts, dates, and non-positive prices/quantities.
Generates comprehensive Data Quality Reports.
"""

import pandas as pd
from typing import Dict, Any

class DataValidator:
    """
    Validates E-Commerce DataFrame and returns structured data quality issues and reports.
    """
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.report: Dict[str, Any] = {}

    def run_validation(self) -> Dict[str, Any]:
        """Runs full validation suite and returns data quality dictionary."""
        total_rows = len(self.df)
        
        # Missing values check
        missing_counts = self.df.isnull().sum().to_dict()
        rows_with_missing = int(self.df.isnull().any(axis=1).sum())
        
        # Duplicate rows check
        duplicate_count = int(self.df.duplicated().sum())
        
        # Invalid numeric checks
        invalid_quantities = 0
        if "quantity" in self.df.columns:
            invalid_quantities = int((pd.to_numeric(self.df["quantity"], errors="coerce") <= 0).sum())
            
        invalid_prices = 0
        if "unit_price" in self.df.columns:
            invalid_prices = int((pd.to_numeric(self.df["unit_price"], errors="coerce") <= 0).sum())
            
        invalid_discounts = 0
        if "discount" in self.df.columns:
            disc_series = pd.to_numeric(self.df["discount"], errors="coerce")
            invalid_discounts = int(((disc_series < 0) | (disc_series > 1.0)).sum())
            
        # Invalid date formats
        invalid_dates = 0
        if "order_date" in self.df.columns:
            converted_dates = pd.to_datetime(self.df["order_date"], errors="coerce")
            invalid_dates = int(converted_dates.isnull().sum())

        self.report = {
            "total_records": total_rows,
            "rows_with_missing_values": rows_with_missing,
            "missing_column_counts": missing_counts,
            "duplicate_records": duplicate_count,
            "invalid_quantities": invalid_quantities,
            "invalid_unit_prices": invalid_prices,
            "invalid_discounts": invalid_discounts,
            "invalid_dates": invalid_dates,
            "overall_status": "PASSED" if (
                rows_with_missing == 0 and
                duplicate_count == 0 and
                invalid_quantities == 0 and
                invalid_prices == 0 and
                invalid_discounts == 0 and
                invalid_dates == 0
            ) else "WARNINGS_FOUND"
        }
        return self.report

    def print_summary(self):
        """Prints formatted Data Quality Report."""
        if not self.report:
            self.run_validation()
            
        rep = self.report
        print("==================================================")
        print("           DATA QUALITY VALIDATION REPORT         ")
        print("==================================================")
        print(f"Total Input Records      : {rep['total_records']}")
        print(f"Overall Status           : {rep['overall_status']}")
        print(f"Duplicate Rows           : {rep['duplicate_records']}")
        print(f"Rows with Missing Values : {rep['rows_with_missing_values']}")
        print(f"Invalid Quantities (<=0) : {rep['invalid_quantities']}")
        print(f"Invalid Unit Prices (<=0): {rep['invalid_unit_prices']}")
        print(f"Invalid Discounts (<0/>1): {rep['invalid_discounts']}")
        print(f"Invalid Order Dates      : {rep['invalid_dates']}")
        print("--------------------------------------------------")
        print("Missing Values by Column:")
        for col, cnt in rep["missing_column_counts"].items():
            if cnt > 0:
                print(f"  - {col:18s}: {cnt}")
        print("==================================================")
