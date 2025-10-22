import pandas as pd

def format_value(value):
    """Format value to show in thousand, million or billion"""
    try:
        val = float(value)
        if val >= 1_000_000_000:  # Billion
            return f"{val / 1_000_000_000:.1f} miliar"
        elif val >= 1_000_000:  # Million
            return f"{val / 1_000_000:.1f} jt"
        elif val >= 1_000:  # Thousand
            return f"{val / 1_000:.1f} rb"
        else:
            return f"{val:,.0f}"
    except:
        return str(value)

def format_percentage(value):
    """Convert value to percentage format for RBC"""
    try:
        return f"{float(value*100):.2f}%"
    except:
        return f"{value*100}%"

def null_value(value):
    """Return 0 if value is NaN or '-', otherwise return the value"""
    if pd.isna(value) or value == "-" or value == "":
        return 0
    return value
