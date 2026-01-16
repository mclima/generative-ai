def format_salary(salary_min=None, salary_max=None, currency="USD", period="year", is_estimated=False):
    """Format salary range into a readable string with optional estimation indicator"""
    if not salary_min and not salary_max:
        return None
    
    period_lower = period.lower() if period else "year"
    
    if salary_min and salary_max:
        salary_str = f"{currency} {salary_min:,.0f} - {salary_max:,.0f} per {period_lower}"
    elif salary_min:
        salary_str = f"{currency} {salary_min:,.0f}+ per {period_lower}"
    elif salary_max:
        salary_str = f"Up to {currency} {salary_max:,.0f} per {period_lower}"
    else:
        return None
    
    # Append estimation indicator if applicable
    if is_estimated:
        salary_str = f"{salary_str} (estimated)"
    
    return salary_str
