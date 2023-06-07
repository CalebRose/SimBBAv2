import re


def Get_Inches(height):
    r = re.compile(r"([0-9]+)-([0-9]+)")
    m = r.match(height)
    if m == None:
        return float("NaN")
    else:
        return int(m.group(1)) * 12 + float(m.group(2))
