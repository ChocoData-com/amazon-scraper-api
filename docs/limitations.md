# Limitations

This repo is deliberately minimal. Here's what will break, when, and why.

## Things that will stop working

### 1. Amazon's robot page ("Enter the characters you see below")

**Frequency:** common from datacenter IPs, occasional from residential. The examples in this repo will print `error: Amazon showed a robot check` and exit 1.

**Fix (partial):** use a residential-IP proxy via the `PROXY_URL` env var. Even then, Amazon serves robot pages ~5–15% of the time on residential IPs. You'd need retry logic + multi-tier proxy failover to get this rate down.

**Fix (proper):** the [managed service](https://amazonscraperapi.com) auto-detects robot pages and retries through escalating proxy tiers (datacenter → residential → premium stealth), transparently.

### 2. CSS selector rot

Amazon's DOM changes roughly monthly. Class names like `.a-price-whole` drift or get renamed. When that happens, this repo's extractors silently return `None` / empty.

**Signal:** you get a `warning: extraction returned no title` message. Or title is present but `price` is `null`.

**Fix here:** submit a PR with the new selector. We'll merge.

**Fix proper:** the managed service has the entire extractor library updated as Amazon changes things. Your code never sees the churn.

### 3. Marketplace quirks

This repo tries three domains (`com`, `de`, `co.uk`). It will **not** work well on:

- `amazon.co.jp` — price uses `¥` prefix, different layout
- `amazon.com.br` — Portuguese labels, different price format
- `amazon.in` — `₹` currency, decimal separator quirks
- `amazon.com.au` — GST-inclusive prices, different review display
- Amazon Fresh / Whole Foods listings — completely different templates
- Electronics vs books vs grocery — Amazon uses different product templates

**Fix here:** contribute marketplace-specific parsing if you're motivated.

**Fix proper:** managed service supports 20+ marketplaces with per-marketplace extractors.

### 4. Rate limiting per IP

If you run the Python/Node example in a tight loop from one IP, Amazon will start dropping your requests or shadow-banning. The examples do **not** implement backoff, retries, or IP rotation.

**Fix here:** add your own rate limiter. Recommend `asyncio.Semaphore(5)` max concurrent, 2s sleep between requests per proxy.

**Fix proper:** managed service handles concurrency per plan (free = 10 parallel, Indie = 50, Team = 50, Scale = 100) automatically, with a built-in request-rate budget.

### 5. Personalized content

Amazon personalizes prices, recommendations, and even product details by user cohort. A "clean" proxy (no cookies, fresh IP) sees different content than a logged-in US Prime member. The examples get the "clean" view, which is often what you want for competitive intelligence but **not** what an actual customer sees.

**Nothing to fix here at this repo's level** — personalization is a property of Amazon's CDN, not your scraper. Managed services can't bypass it either; they just serve the "clean" view consistently.

## Things that are fundamentally out of scope

This repo will never implement (PRs adding them will be politely closed):

- **Structured review extraction** — individual review text, helpful-count, verified-purchase flag, 1-star vs 5-star breakdowns
- **Variant tree** — all color/size/storage ASINs and their prices
- **A+ content** — the rich description blocks sellers pay for
- **Buy Box scraping** — who owns the buybox, seller ratings, prime eligibility per offer
- **Offer listings** — the "other sellers on Amazon" sidebar
- **Spec tables** — the product information table at the bottom of the listing
- **Q&A section** — customer questions and answers
- **Sponsored placements** — ads vs organic in search results
- **Category browsing / bestseller scraping**
- **Async job queueing with webhook callback**
- **TLS fingerprinting / JA3 impersonation**

All of these are in the [managed service](https://amazonscraperapi.com) as first-class features. That's the whole point of the split: this repo teaches you the basics, the managed service handles the production surface.

## When you've outgrown this repo

Signs you should move to the managed service:

- You've added >100 lines on top of the examples and half of it is retry/CAPTCHA/proxy rotation logic
- You're debugging Amazon DOM changes more than once a month
- You need data from more than 2 marketplaces
- You need reviews, variants, or Buy Box (not just title/price)
- Your scraper "works on my machine" but customers are getting stale data
- You want a webhook when your 10,000-ASIN batch finishes, not a polling loop

Signing up is free: https://app.amazonscraperapi.com. 1,000 requests to validate it fits your use case, no card required.
