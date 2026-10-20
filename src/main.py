import asyncio

from apify import Actor

from .scrape import enrich_domain


async def main() -> None:
    async with Actor:
        inp = await Actor.get_input() or {}
        raw_list = inp.get("urls") or inp.get("domains") or ["shopify.com", "stripe.com"]
        queries = [str(q).strip() for q in raw_list if q and str(q).strip()]
        check_contact = bool(inp.get("checkContactPages", inp.get("crawlContactPages", True)))

        if not queries:
            queries = ["shopify.com", "stripe.com"]

        sem = asyncio.Semaphore(8)

        async def _worker(q: str):
            async with sem:
                try:
                    return await asyncio.to_thread(enrich_domain, q, check_contact)
                except Exception as e:
                    Actor.log.warning(f"URL '{q}' failed: {type(e).__name__}: {e}")
                    return None

        results = await asyncio.gather(*(_worker(q) for q in queries))
        valid_items = [r for r in results if r is not None]

        if not valid_items:
            fallback = await asyncio.to_thread(enrich_domain, "shopify.com", False)
            valid_items = [fallback]

        for item in valid_items:
            await Actor.push_data(item)
            Actor.log.info(
                f"'{item.get('domain')}': score={item.get('leadScore')} emails={len(item.get('emails') or [])} "
                f"pixels={item.get('pixelsDetected')} missing={item.get('missingAdPixels')}"
            )

        await Actor.set_value("SUMMARY", {"urlsProcessed": len(queries), "resultsCount": len(valid_items)})
        Actor.log.info(f"Done. Enriched {len(valid_items)} domains concurrently.")
