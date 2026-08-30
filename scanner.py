import re
from urllib.parse import urlparse

URL_RE = re.compile(r'(?:(?:https?://)|(?:www\.))[^\s<>"\']+', re.I)

KEYWORDS = {
    "urgent": ["urgent", "immediately", "asap", "act now", "last warning", "today only", "expire today", "suspended today", "now na", "agad", "kaagad", "hurry", "limited time"],
    "credential": ["otp", "one-time password", "pin", "password", "passcode", "cvv", "card number", "bank details", "verification code"],
    "account_threat": ["account suspended", "account blocked", "account locked", "deactivated", "will be suspended", "verify your account", "update your account", "reactivate"],
    "prize": ["congratulations", "you won", "winner", "claim your prize", "free load", "cash prize", "reward"],
    "payment": ["pay now", "unpaid", "outstanding balance", "refund", "release your funds", "processing fee"],
    "impersonation": ["gcash", "maya", "bdo", "bpi", "metrobank", "unionbank", "bank", "lazada", "shopee", "philpost", "dhl", "j&t", "government"],
}

URL_SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "is.gd", "cutt.ly",
    "shorturl.at", "rb.gy", "rebrand.ly"
}

SUSPICIOUS_TLDS = {".xyz", ".top", ".click", ".link", ".live", ".buzz", ".shop", ".online"}

def clean_url(url):
    return url.rstrip(".,!?;:)]}")

def extract_urls(text):
    return [clean_url(u) for u in URL_RE.findall(text)]

def is_suspicious_url(url):
    candidate = url if url.startswith(("http://", "https://")) else "http://" + url
    host = (urlparse(candidate).hostname or "").lower()
    reasons = []

    if host in URL_SHORTENERS:
        reasons.append("URL shortener detected")

    if re.match(r"^\d{1,3}(?:\.\d{1,3}){3}$", host):
        reasons.append("IP address used instead of a normal domain")

    if any(host.endswith(tld) for tld in SUSPICIOUS_TLDS):
        reasons.append("Uncommon high-risk domain extension")

    if "@" in url:
        reasons.append("Obfuscated URL pattern")

    if host.count("-") >= 2:
        reasons.append("Multiple hyphens in domain")

    return host, reasons

def analyze_sms(text):
    lower = text.lower()
    score = 0
    indicators = []
    categories = {}

    for category, words in KEYWORDS.items():
        matches = [w for w in words if w in lower]
        if matches:
            categories[category] = matches
            if category == "credential":
                score += 30
                indicators.append("Humihingi o tumutukoy sa sensitive credentials gaya ng OTP, PIN, o password.")
            elif category == "account_threat":
                score += 18
                indicators.append("May banta o pressure tungkol sa account suspension/verification.")
            elif category == "urgent":
                score += 12
                indicators.append("May urgent o pressure-based language.")
            elif category == "prize":
                score += 10
                indicators.append("May prize/reward claim language na karaniwang ginagamit sa scam.")
            elif category == "payment":
                score += 10
                indicators.append("May payment/refund/fund release language na dapat i-verify.")
            elif category == "impersonation":
                score += 5
                indicators.append("May pangalan ng kilalang serbisyo o organisasyon; kailangan i-verify ang tunay na sender.")

    urls = extract_urls(text)
    url_details = []

    for url in urls:
        host, reasons = is_suspicious_url(url)
        url_details.append({"url": url, "domain": host, "reasons": reasons})
        if reasons:
            score += 25
            indicators.append(f"Suspicious link detected: {host} ({'; '.join(reasons)}).")
        else:
            score += 8
            indicators.append(f"May external link na dapat i-verify: {host}.")

    if re.search(r"\b\d{4,8}\b", text) and any(k in lower for k in ["otp", "code", "verification"]):
        score += 8

    if len(text) < 15:
        score = max(0, score - 5)

    score = min(score, 100)

    if score >= 76:
        level, label = "HIGH RISK", "high"
        recommendation = "Huwag i-click ang links at huwag magbigay ng OTP, PIN, password, o bank details. I-verify ang mensahe gamit lamang ang official app o website."
    elif score >= 51:
        level, label = "LIKELY SCAM", "likely"
        recommendation = "Malakas ang scam/phishing indicators. Huwag muna mag-click o mag-reply bago ma-verify ang sender."
    elif score >= 26:
        level, label = "SUSPICIOUS", "suspicious"
        recommendation = "May ilang suspicious indicators. I-verify ang sender at domain sa official channels."
    else:
        level, label = "LOW RISK", "low"
        recommendation = "Walang malakas na scam indicator na nakita, ngunit hindi ito garantiya na legitimate ang mensahe."

    if not indicators:
        indicators.append("Walang pangunahing scam pattern na nakita ng current rule-based scanner.")

    return {
        "risk_score": score,
        "risk_level": level,
        "risk_label": label,
        "indicators": indicators,
        "urls": url_details,
        "categories": categories,
        "recommendation": recommendation,
        "disclaimer": "Ang resultang ito ay automated assessment lamang at hindi garantiyang 100% accurate."
    }
