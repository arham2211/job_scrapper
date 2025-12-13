import re
from datetime import datetime, timedelta

def parse_salary(salary_text):
    """
    Parses salary text and returns (min_annual, max_annual) as integers.
    Handles hourly, daily, and annual rates.
    Handles 'k' suffix.
    """
    if not salary_text:
        return None, None
    
    text = salary_text.lower().replace(',', '')
    
    # Search for numbers, possibly with 'k'
    # logical groups: (number) (optional k)
    matches = re.findall(r'(\d+(?:\.\d+)?)\s*(k)?', text)
    
    if not matches:
        return None, None
    
    values = []
    for num_str, k_suffix in matches:
        try:
            val = float(num_str)
            if k_suffix:
                val *= 1000
            values.append(val)
        except ValueError:
            continue
            
    if not values:
        return None, None
        
    # Determine multiplier
    # Default is 1 (Annual)
    multiplier = 1.0
    
    # Check text for period indicators
    if any(x in text for x in ['hour', 'hr', '/h', 'p.h']):
        multiplier = 2080.0  # 40 * 52
    elif any(x in text for x in ['day', 'daily', '/d', 'p.d']):
        multiplier = 260.0   # 5 * 52
    elif any(x in text for x in ['week', 'weekly', '/w']):
        multiplier = 52.0
    elif any(x in text for x in ['month', 'monthly', '/m']):
        multiplier = 12.0
        
    # Heuristic: If values are small (< 200) and no period specified, assume hourly
    if multiplier == 1.0:
        if all(v < 200 for v in values):
            multiplier = 2080.0
    
    annual_values = [v * multiplier for v in values]
    
    # Sort to find range
    annual_values.sort()
    
    if len(annual_values) >= 2:
        # Take min and max
        min_salary = int(annual_values[0])
        max_salary = int(annual_values[-1])
        return min_salary, max_salary
    elif len(annual_values) == 1:
        val = int(annual_values[0])
        return val, val
        
    return None, None

def parse_posted_date(date_text):
    """
    Parses relative date strings like 'Posted 2 days ago' into ISO date string YYYY-MM-DD.
    """
    if not date_text:
        return None
        
    text = date_text.lower()
    now = datetime.now()
    
    try:
        if '30+' in text:
             return (now - timedelta(days=30)).date().isoformat()
             
        # Find number and unit
        match = re.search(r'(\d+)\s*([a-z]+)', text)
        if match:
            num = int(match.group(1))
            unit = match.group(2)
            
            delta = timedelta(0)
            if 'h' in unit: # hours, hr
                delta = timedelta(hours=num)
            elif 'd' in unit: # days, day
                delta = timedelta(days=num)
            elif 'm' in unit and 'mon' not in unit: # minutes, min
                delta = timedelta(minutes=num)
            elif 'w' in unit: # weeks
                delta = timedelta(weeks=num)
            elif 'mon' in unit: # months
                delta = timedelta(days=num*30)
            elif 'y' in unit: # years
                delta = timedelta(days=num*365)
                
            return (now - delta).date().isoformat()
            
    except Exception:
        pass
        
    return None
