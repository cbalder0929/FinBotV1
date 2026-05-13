"""
Rule-based categorizer for deterministic merchant patterns.

Known, repeatable merchant matches are handled here before transactions are
sent to AI. Claude is reserved for ambiguous descriptions that need judgment.
"""

import re

CATEGORY_EMOJIS = {
    "Food": "\U0001F6D2",
    "Dining": "\U0001F354",
    "Transport": "\U0001F687",
    "Cannabis": "\U0001F33F",
    "Utilities": "⚡",
    "Shopping": "\U0001F6CD️",
    "Health": "\U0001F48A",
    "Entertainment": "\U0001F3AE",
    "Income": "\U0001F4B0",
    "Other": "\U0001F4E6",
}

# Order matters: more-specific rules should appear first.
RULES: list[tuple[re.Pattern, str]] = [
    # Cannabis dispensaries
    (re.compile(r"\b(sunnyside|zen\s?leaf|dispensary|cresco|cannabis|medmen|rise\s?disp|verilife|ascend\s?well|nuera|curaleaf)\b", re.I), "Cannabis"),

    # Grocery / food retail
    (re.compile(r"\b(marianos?|jewel|aldi|whole\s?foods?|trader\s?joe|costco|kroger|walmart\s?gro|safeway|publix|wegmans|sprouts|fresh\s?market|stop\s?shop|food\s?lion|harris\s?teeter)\b", re.I), "Food"),

    # Transportation / rideshare / transit / fuel
    (re.compile(r"\b(uber(?!\s?eats)|lyft|cta|ventra|greyhound|amtrak|metra|transit|sound\s?transit|bart|mta|wmata|septa|hertz|enterprise|avis|budget\s?rent|zipcar|spothero|parkmobile|shell|chevron|exxon|mobil|bp\s|sunoco|valero|marathon|circle\s?k|7-?eleven|wawa|speedway)\b", re.I), "Transport"),

    # Dining / restaurants / coffee shops / fast food
    (re.compile(r"\b(portillos?|starbucks|chipotle|mcdonald|domino|pizza|restaurant|cafe|grill|taco\s?bell|burger\s?king|wendy|kfc|popeye|chick.fil.a|panera|dunkin|tim\s?horton|five\s?guys|in.n.out|shake\s?shack|sweet\s?green|cava|qdoba|moe.s|jersey\s?mike|jimmy\s?john|subway|panda\s?express|olive\s?garden|outback|texas\s?roadhouse|cheesecake|applebee|chili.s|denny|ihop|waffle\s?house|cracker\s?barrel|red\s?lobster|red\s?robin|buffalo\s?wild|uber\s?eats|doordash|grubhub|caviar|postmates|seamless|instacart\s?dining)\b", re.I), "Dining"),

    # Utilities / telecom / streaming-only-as-utility (cable internet)
    (re.compile(r"\b(comed|com\s?ed|at&t|comcast|xfinity|nicor|verizon|t.mobile|sprint|spectrum|cox\s?comm|centurylink|frontier|optimum|directv|dish\s?net|peoples\s?gas|nicor\s?gas|water|sewer|electric\s?co|gas\s?co|utility)\b", re.I), "Utilities"),

    # Shopping / retail / online
    (re.compile(r"\b(amazon|amzn|target|walmart(?!\s?gro)|best\s?buy|macy|nordstrom|gap\s|h&m|zara|old\s?navy|kohl|tj\s?max|marshall|home\s?depot|lowe.s|menards|ikea|wayfair|etsy|ebay|costco\s?wholesale|sam.s\s?club|bj.s\s?wholesale|apple\.com|apple\s?store|microsoft\s?store|paypal\s+|venmo\s+(?!from)|shopify|stripe\s+chk)\b", re.I), "Shopping"),

    # Health / pharmacy / medical
    (re.compile(r"\b(cvs|walgreen|rite\s?aid|hospital|medical|pharmacy|dental|doctor|clinic|kaiser|blue\s?cross|aetna|cigna|humana|labcorp|quest\s?diag|walgreen|gnc|vitamin\s?shop)\b", re.I), "Health"),

    # Entertainment / subscriptions / streaming / gaming
    (re.compile(r"\b(netflix|spotify|hulu|disney(?:\s?plus|\+)?|hbo\s?max|max\s?stream|apple\s?tv|paramount\+|peacock|youtube\s?prem|steam(?:\s?games)?|playstation|xbox|nintendo|epic\s?games|twitch|patreon|substack|audible|kindle|apple\s?music|amazon\s?music|tidal|sirius|pandora|amc(?!\s?card)|cinemark|regal|alamo|ticketmaster|stubhub|seatgeek|live\s?nation|concert|theater|theatre)\b", re.I), "Entertainment"),

    # Income
    (re.compile(r"\b(direct\s?deposit|payroll|salary|zelle\s+from|venmo\s+from|cash\s?app\s+from|tax\s?ref|refund|interest\s?paid|dividend|reimburs)\b", re.I), "Income"),
]


def category_emoji(category: str) -> str:
    return CATEGORY_EMOJIS.get(category, CATEGORY_EMOJIS["Other"])


def rule_based_category(description: str) -> tuple[str, str]:
    for pattern, category in RULES:
        if pattern.search(description):
            return category, category_emoji(category)
    return "Other", category_emoji("Other")


def clean_merchant(description: str) -> str:
    merchant = re.sub(r"\b\d{4,}\b", "", description)         # drop long digit runs
    merchant = re.sub(r"#\d+", "", merchant)                   # drop store-id like "#1234"
    merchant = re.sub(r"\s+", " ", merchant).strip(" -*.,")
    return merchant[:40] or description[:40]
