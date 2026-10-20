"""Core logic: B2B Website Contact, WhatsApp, Socials & Ad-Pixel / Tech-Stack Lead Enricher.

Crawls a domain's homepage and up to 2 high-signal contact/about pages using fast HTTP requests,
extracting:
- Verified emails, phone numbers, WhatsApp links
- Social media profiles (LinkedIn, Instagram, TikTok, Facebook, X/Twitter, YouTube)
- Ad Pixels installed (Meta Pixel, TikTok Pixel, Google Ads Tag, GTM, GA4, LinkedIn Insight, Pinterest Tag)
- E-commerce & CRM tech stack (Shopify, WooCommerce, WordPress, Webflow, Wix, Klaviyo, HubSpot, Intercom)
- Missing ad pixels (instant pitch angle for marketing agencies & SDRs)
"""
from __future__ import annotations

import html
import re
import urllib.parse
from typing import Any

import requests

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,12}")
_JUNK_EMAIL_EXT = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".css", ".js", ".woff", ".ttf")
_JUNK_EMAIL_DOMAINS = {"example.com", "domain.com", "email.com", "yoursite.com", "sentry.io", "wixpress.com"}

_SOCIAL_PATTERNS = {
    "linkedin": re.compile(r"https?://(?:www\.)?linkedin\.com/(?:company|in)/[a-zA-Z0-9_\-%]+", re.I),
    "instagram": re.compile(r"https?://(?:www\.)?instagram\.com/[a-zA-Z0-9_.\-]+", re.I),
    "facebook": re.compile(r"https?://(?:www\.)?facebook\.com/[a-zA-Z0-9_.\-]+", re.I),
    "tiktok": re.compile(r"https?://(?:www\.)?tiktok\.com/@[a-zA-Z0-9_.\-]+", re.I),
    "twitter": re.compile(r"https?://(?:www\.)?(?:twitter\.com|x\.com)/[a-zA-Z0-9_]+", re.I),
    "youtube": re.compile(r"https?://(?:www\.)?youtube\.com/(?:@[a-zA-Z0-9_.\-]+|channel/[a-zA-Z0-9_\-]+|c/[a-zA-Z0-9_\-]+)", re.I),
}

_WA_RE = re.compile(r"https?://(?:wa\.me|api\.whatsapp\.com/send)\S+", re.I)
_TEL_RE = re.compile(r'href=["\']tel:([^"\']+)["\']', re.I)
_TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)
_DESC_RE = re.compile(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']', re.I)

_PIXEL_SIGNATURES = {
    "Meta Pixel": ("connect.facebook.net", "fbevents.js", "fbq("),
    "TikTok Pixel": ("analytics.tiktok.com", "ttq.load"),
    "Google Ads Tag": ("googleadservices.com", "googlesyndication.com", "gtag('config', 'AW-", 'gtag("config", "AW-'),
    "Google Tag Manager": ("googletagmanager.com/gtm.js", "GTM-"),
    "Google Analytics (GA4)": ("googletagmanager.com/gtag/js", "gtag('config', 'G-", 'gtag("config", "G-'),
    "LinkedIn Insight": ("snap.licdn.com/li.lms-analytics", "_linkedin_partner_id"),
    "Pinterest Tag": ("s.pinimg.com/ct/core.js", "pintrk("),
}

_TECH_SIGNATURES = {
    "Shopify": ("cdn.shopify.com", "Shopify.theme", "myshopify.com"),
    "WooCommerce": ("woocommerce", "wp-content/plugins/woocommerce"),
    "WordPress": ("wp-content/", "wp-includes/"),
    "Webflow": ("webflow.com", "data-wf-site"),
    "Wix": ("wix.com", "wixstatic.com"),
    "Squarespace": ("squarespace.com", "static1.squarespace.com"),
    "Klaviyo": ("klaviyo.com", "static.klaviyo.com"),
    "HubSpot": ("js.hs-scripts.com", "js.hsforms.net", "hubspot"),
    "Intercom": ("widget.intercom.io", "Intercom("),
    "Crisp Chat": ("client.crisp.chat", "CRISP_WEBSITE_ID"),
    "Stripe": ("js.stripe.com",),
}


def normalize_url(raw: str) -> str:
    s = (raw or "").strip()
    if not s:
        return ""
    if not s.startswith(("http://", "https://")):
        s = "https://" + s
    return s


def fetch_html(url: str, timeout: int = 12) -> str:
    resp = requests.get(
        url,
        headers={
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,id;q=0.8",
        },
        timeout=timeout,
        allow_redirects=True,
    )
    resp.raise_for_status()
    return resp.text[:600_000]


def clean_emails(raw_emails: list[str]) -> list[str]:
    seen = set()
    out = []
    for e in raw_emails:
        el = e.strip().lower().rstrip(".")
        if any(el.endswith(ext) for ext in _JUNK_EMAIL_EXT):
            continue
        dom = el.split("@")[-1]
        if dom in _JUNK_EMAIL_DOMAINS or "sentry" in dom or "webpack" in el:
            continue
        if el not in seen:
            seen.add(el)
            out.append(el)
    return out[:20]


def enrich_domain(raw_query: str, check_contact_pages: bool = True) -> dict[str, Any]:
    url = normalize_url(raw_query)
    parsed = urllib.parse.urlparse(url)
    domain = (parsed.netloc or raw_query).lower()
    if domain.startswith("www."):
        domain = domain[4:]
    base_origin = f"{parsed.scheme}://{parsed.netloc}"

    pages_html = []
    status = "ok"
    try:
        home_html = fetch_html(url)
        pages_html.append(home_html)
    except Exception as e:
        status = f"unreachable ({type(e).__name__})"
        home_html = ""

    if home_html and check_contact_pages:
        for path in ("/contact", "/contact-us", "/pages/contact-us", "/pages/contact", "/about", "/hubungi-kami"):
            if len(pages_html) >= 2:
                break
            if path in home_html.lower():
                try:
                    sub = fetch_html(base_origin + path, timeout=8)
                    if sub:
                        pages_html.append(sub)
                except Exception:
                    pass

    combined = "\n".join(pages_html)
    title_m = _TITLE_RE.search(home_html)
    desc_m = _DESC_RE.search(home_html)
    title = html.unescape(re.sub(r"\s+", " ", title_m.group(1)).strip())[:200] if title_m else None
    meta_desc = html.unescape(desc_m.group(1).strip())[:300] if desc_m else None

    emails = clean_emails(_EMAIL_RE.findall(combined))
    phones = list(dict.fromkeys(p.strip() for p in _TEL_RE.findall(combined) if len(p.strip()) >= 6))[:10]
    wa_links = list(dict.fromkeys(w.rstrip("\"' >)") for w in _WA_RE.findall(combined)))[:5]

    socials: dict[str, str | None] = {}
    for k, pat in _SOCIAL_PATTERNS.items():
        matches = [m for m in pat.findall(combined) if not m.lower().endswith(("/share", "/sharer", "/intent"))]
        socials[k] = matches[0] if matches else None

    pixels_detected = [
        name for name, sigs in _PIXEL_SIGNATURES.items() if any(sig in combined for sig in sigs)
    ]
    core_ad_pixels = ["Meta Pixel", "TikTok Pixel", "Google Ads Tag"]
    missing_ad_pixels = [p for p in core_ad_pixels if p not in pixels_detected]

    tech_stack = [
        name for name, sigs in _TECH_SIGNATURES.items() if any(sig in combined for sig in sigs)
    ]

    lead_score = 15
    if emails:
        lead_score += 30
    if phones or wa_links:
        lead_score += 15
    if any(socials.values()):
        lead_score += 10
    if pixels_detected:
        lead_score += 15
    if missing_ad_pixels:
        lead_score += 15
    lead_score = min(100, lead_score)

    active_ads_str = ", ".join(pixels_detected[:3]) if pixels_detected else "no tracking pixels"
    missing_str = " or ".join(missing_ad_pixels[:2]) if missing_ad_pixels else "cross-channel attribution"
    stack_str = tech_stack[0] if tech_stack else "website"
    if pixels_detected and missing_ad_pixels:
        pitch_hook = (
            f"Noticed {domain} ({stack_str}) is active with {active_ads_str} but missing {missing_str} "
            f"— great opportunity to capture retargeting ROAS across untapped channels."
        )
    elif not pixels_detected:
        pitch_hook = (
            f"Noticed {domain} ({stack_str}) currently has no Meta, TikTok, or Google Ads conversion pixels installed "
            f"— prime candidate for paid acquisition and tracking setup."
        )
    else:
        pitch_hook = (
            f"Saw {domain} ({stack_str}) is running a full ad pixel stack ({active_ads_str}) "
            f"— pitch creative testing, server-side CAPI tracking, or CRO."
        )

    return {
        "domain": domain,
        "url": url,
        "status": status,
        "title": title,
        "description": meta_desc,
        "leadScore": lead_score,
        "agencyPitchHook": pitch_hook,
        "emails": emails,
        "primaryEmail": emails[0] if emails else None,
        "phones": phones,
        "whatsappLinks": wa_links,
        "hasWhatsApp": bool(wa_links),
        "linkedin": socials["linkedin"],
        "instagram": socials["instagram"],
        "facebook": socials["facebook"],
        "tiktok": socials["tiktok"],
        "twitter": socials["twitter"],
        "youtube": socials["youtube"],
        "pixelsDetected": pixels_detected,
        "hasMetaPixel": "Meta Pixel" in pixels_detected,
        "hasTikTokPixel": "TikTok Pixel" in pixels_detected,
        "hasGoogleAdsTag": "Google Ads Tag" in pixels_detected,
        "hasGTM": "Google Tag Manager" in pixels_detected,
        "missingAdPixels": missing_ad_pixels,
        "techStack": tech_stack,
    }
