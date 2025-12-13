from utils import parse_salary, parse_posted_date
from datetime import datetime, timedelta

def test_salary():
    cases = [
        ("$100k - $120k", (100000, 120000)),
        ("100,000 - 120,000", (100000, 120000)),
        ("$50 per hour", (104000, 104000)), # 50 * 2080
        ("$800 per day", (208000, 208000)), # 800 * 260
        ("80k + super", (80000, 80000)),
        ("Some text", (None, None)),
        ("$100000", (100000, 100000)),
        ("$30.50/hr", (63440, 63440)), # 30.5 * 2080 = 63440.0
    ]
    
    print("Testing Salary Parsing:")
    for inp, expected in cases:
        result = parse_salary(inp)
        status = "✅" if result == expected else f"❌ Expected {expected}, got {result}"
        print(f"  '{inp}' -> {result} {status}")

def test_date():
    print("\nTesting Date Parsing:")
    cases = [
        ("Posted 2 days ago", (datetime.now() - timedelta(days=2)).date().isoformat()),
        ("Posted 5 hours ago", datetime.now().date().isoformat()),
        ("Posted yesterday", (datetime.now() - timedelta(days=1)).date().isoformat()),
        ("30+ days ago", (datetime.now() - timedelta(days=30)).date().isoformat()),
        ("Posted 1w ago", (datetime.now() - timedelta(weeks=1)).date().isoformat()),
    ]
    
    for inp, expected in cases:
        result = parse_posted_date(inp)
        status = "✅" if result == expected else f"❌ Expected {expected}, got {result}"
        print(f"  '{inp}' -> {result} {status}")

if __name__ == "__main__":
    test_salary()
    test_date()
