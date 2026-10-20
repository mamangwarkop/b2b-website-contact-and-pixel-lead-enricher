# B2B Website Contact, Socials & Ad-Pixel Lead Enricher

Turn raw company domain lists (from **Google Maps, Apollo, Clay, LinkedIn, or CSVs**) into **pitch-ready B2B agency leads** in seconds. Automatically extracts **verified business emails, phone numbers, clickable WhatsApp (`wa.me`) links, 6 social media channels, installed Ad Pixels, `missingAdPixels`, E-Commerce/CRM tech stack, B2B `leadScore` (0–100), and a personalized `agencyPitchHook`** — with **zero browser overhead**.

---

## Why Choose This Actor Over Standard Website Contact Scrapers?

| Feature | Our Actor (`mamang_warkop`) | Standard Email / Contact Scrapers |
| :--- | :--- | :--- |
| **Multi-Channel Contact Extraction** | Extracts **Emails + Phones + WhatsApp (`wa.me`) + LinkedIn, Instagram, TikTok, Facebook, X, YouTube**. | Emails and social links only (rarely extracts WhatsApp links). |
| **Ad-Pixel & Retargeting Radar** | Detects **Meta Pixel, TikTok Pixel, Google Ads Tag, GTM, GA4, LinkedIn Insight, Pinterest Tag**. | None — requires a separate technographics tool ($50+/mo). |
| **Missing Ad-Pixel Pitch Signal** | Automatically outputs **`missingAdPixels`** (e.g. runs Meta Pixel, missing TikTok & Google Ads) so agencies know *exactly* what service to pitch. | Not available. |
| **Ready-to-Send `agencyPitchHook`** | Generates a **1-sentence personalized cold email icebreaker** tailored to the prospect's tech stack and pixel gaps. | Raw data only. |
| **Smart Contact Sub-Page Crawling** | Automatically checks homepage + `/contact`, `/contact-us`, `/pages/contact-us`, `/about`, and `/hubungi-kami`. | Often misses emails hidden on `/contact` pages. |
| **High-Speed Async Engine** | Concurrent HTTP architecture enriches **100 domains in ~12–15 seconds** at minimal compute cost. | Slow headless browsers that cost 10x more compute credits. |

---

## Step-by-Step Usage Guide (Panduan Penggunaan)

### Option A: Run in Apify Console UI (Zero Coding)
1. **Paste Target Domains (`urls`):** Enter a list of company domains or URLs (`gymshark.com`, `colourpop.com`, `https://kopikenangan.com`).
2. **Enable Contact Sub-Pages (`checkContactPages`):** Leave checked (`true`) so the Actor automatically inspects `/contact` and `/about` pages whenever the homepage doesn't list an email directly.
3. Click **Start**, then export your enriched lead table in **CSV, Excel, or JSON** from the **Dataset** tab.

---

### Option B: Automate Inside Clay.com, n8n, or Make.com
Connect this Actor right after a **Google Maps Scraper** or **Apollo/LinkedIn Domain Export** via a single HTTP POST call:

```bash
curl -X POST "https://api.apify.com/v2/acts/mamang_warkop~b2b-website-contact-and-pixel-lead-enricher/run-sync-get-dataset-items?token=YOUR_APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["gymshark.com", "colourpop.com", "stripe.com"],
    "checkContactPages": true
  }'
```

---

### Option C: Python & JavaScript SDK

#### Python
```python
from apify_client import ApifyClient

client = ApifyClient("YOUR_APIFY_API_TOKEN")
run = client.actor("mamang_warkop/b2b-website-contact-and-pixel-lead-enricher").call(
    run_input={
        "urls": ["gymshark.com", "colourpop.com"],
        "checkContactPages": True,
    }
)

for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(item["domain"], item["primaryEmail"], item["missingAdPixels"], item["agencyPitchHook"])
```

---

## Input Parameters Reference

| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `urls` | `array` | `["shopify.com", "stripe.com"]` | List of company domains (`example.com`) or full URLs (`https://example.com`). |
| `checkContactPages` | `boolean` | `true` | Automatically crawl `/contact`, `/contact-us`, `/pages/contact-us`, and `/about` pages to maximize email and WhatsApp discovery. |

---

## Sample Output JSON
```json
{
  "domain": "colourpop.com",
  "url": "https://colourpop.com",
  "status": "ok",
  "title": "ColourPop Cosmetics",
  "leadScore": 100,
  "agencyPitchHook": "Noticed colourpop.com (Shopify) is active with Meta Pixel, TikTok Pixel, Google Tag Manager but missing Google Ads Tag — great opportunity to capture retargeting ROAS across untapped channels.",
  "primaryEmail": "support@colourpop.com",
  "emails": ["support@colourpop.com", "pr@colourpop.com"],
  "phones": ["+1-800-555-0199"],
  "whatsappLinks": [],
  "hasWhatsApp": false,
  "linkedin": "https://www.linkedin.com/company/colourpop-cosmetics",
  "instagram": "https://www.instagram.com/colourpopcosmetics",
  "tiktok": "https://www.tiktok.com/@colourpopco",
  "facebook": "https://www.facebook.com/ColourPopCosmetics",
  "twitter": "https://x.com/ColourPopCo",
  "youtube": "https://www.youtube.com/@colourpopcosmetics",
  "pixelsDetected": ["Meta Pixel", "TikTok Pixel", "Google Tag Manager", "Google Analytics (GA4)", "Pinterest Tag"],
  "hasMetaPixel": true,
  "hasTikTokPixel": true,
  "hasGoogleAdsTag": false,
  "hasGTM": true,
  "missingAdPixels": ["Google Ads Tag"],
  "techStack": ["Shopify", "Klaviyo"]
}
```

---

## Transparent Pricing
- **Pay-Per-Event:** `$0.002` per enriched domain (`$2.00 per 1,000 domains`).
- Apify's free `$5.00` monthly credit covers up to **2,500 enriched B2B domains every month for free**.
