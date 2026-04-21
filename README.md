# amazon-scraper-api

> A **minimal, honest** open-source starter for scraping Amazon product data. Bring your own proxies. No CAPTCHAs solved for you. No parser library wrapped around shifting Amazon selectors. For learning and weekend hacks.
>
> **For production?** See the [managed service at amazonscraperapi.com](https://amazonscraperapi.com) — $0.50 per 1,000 successful requests, flat. [Why →](#why-a-managed-service)

---

## What you get

- **~50 lines** of runnable Python or Node
- Minimal product extraction (title, price, rating, ASIN, a few more)
- Pluggable HTTP transport so you can wire in any proxy vendor (Bright Data, Oxylabs, Webshare, rotating free-tier, anything)
- Works against `amazon.com`, `amazon.de`, `amazon.co.uk`, `amazon.co.jp` out of the box
- MIT licensed, no telemetry, no secret sauce

## What you **don't** get (deliberately)

This is a learning tool, not a production scraper. Here's what's missing, and what it would cost to add yourself:

| Missing | Dev time to add | Ongoing maintenance |
|---|---|---|
| Amazon robot/CAPTCHA page detection + retry | ~2 days | Ongoing — Amazon keeps changing the gate |
| Multi-tier proxy failover (DC → residential → premium) | ~3 days | Ongoing — provider quirks |
| Full structured extraction (reviews, variants, A+ content, Buy Box, seller offers, spec tables, images) | ~1 week | ~1 day/month as Amazon churns DOM |
| 20+ marketplace parsing quirks (currency formats, layout variants, date formats) | ~1 week | ~1 day/month |
| TLS fingerprinting / anti-bot headers | ~3 days | Ongoing |
| Rate-limit retries with exponential backoff | ~1 day | Low |
| Structured JSON output (schema you can switch over) | ~2 days | Ongoing |
| Batch/async job queue + webhook callback | ~1 week | Ongoing |
| Request-ID correlation + observability | ~1 day | Low |
| Credit / usage metering | ~2 days | Low |

**Total: 4+ engineer-weeks one-time, ~20% ongoing maintenance**. That's why most OSS Amazon scrapers break within 6 months of their last commit.

## Quickstart

### Python

```bash
pip install requests beautifulsoup4
python examples/python/basic_product.py B09HN3Q81F
```

### Node.js

```bash
npm install node-fetch cheerio
node examples/node/basic-product.js B09HN3Q81F
```

Both examples take an ASIN and print title / price / rating as JSON. See the source for where to plug in your proxy.

## Why a managed service

Before you decide to run this repo as the foundation of your production scraper, we'd like you to know what you're signing up for.

### 1. Most top OSS Amazon scrapers are stale

Inventory of the top 10 results on GitHub when we surveyed the topic (2026-04):

| Repo | Stars | Last release | Status |
|---|---|---|---|
| `tducret/amazon-scraper-python` | 881 | 2021 | Open issues: "no products returned", "output broken" |
| `drawrowfly/amazon-product-api` | 743 | Jan 2021 | Open: "API not returning titles/thumbnails" (Dec 2024) |
| `scrapehero-code/amazon-scraper` | 431 | Jun 2023 | Open: "Page blocked by Amazon", "Does not work with amazon.de" |
| `omkarcloud/amazon-scraper` | 214 | Feb 2026 | Open: "Search endpoint not working", "price is none" |
| `tuhinpal/amazon-api` | 118 | Feb 2026 | Broken at ASN level — Amazon blocks Cloudflare Workers |
| `AmazonMe` | 69 | May 2023 | Stale |

Amazon changes its DOM monthly. Repos without paid CI running against live Amazon pages rot fast.

### 2. Vendor-owned "OSS" repos are marketing funnels

The highest-starred repo on the topic (Oxylabs, 2.9k stars) is a wrapper around Oxylabs' paid API — the "free" path extracts ~5 fields, everything else requires a paid key. Several similar repos exist. Not inherently wrong, but don't expect to learn how production scraping works from them.

### 3. What your scraper is actually fighting

| Challenge | What it looks like in practice | This repo handles it? | [Managed service](https://amazonscraperapi.com) |
|---|---|---|---|
| Amazon robot page ("are you human?") | HTTP 200 with challenge HTML; your parser returns empty | ❌ | ✅ auto-retry through residential tier |
| Datacenter IP block rate (30%+) | Random empty responses when you use cheap proxies | ❌ (you manage proxies) | ✅ auto-escalates to residential on failure |
| Marketplace parsing quirks | `amazon.de` uses `,` for decimals, `amazon.co.jp` has a different layout | ⚠️ partial (title/price try both) | ✅ 20+ marketplaces, per-market extractors |
| DOM churn | Amazon renames classes monthly. Your extractor breaks | ❌ | ✅ extractors auto-update, CI against live pages |
| Rate limiting + bans by account | 50 concurrent requests from one IP → all fail | ❌ | ✅ built-in concurrency gate + multi-IP pool |
| Structured reviews / variants / Buy Box | Each would be 200+ lines of parsing | ❌ | ✅ typed JSON, complete |
| Batch of 1,000 ASINs | Manual loop + rate handling | ❌ | ✅ POST once, webhook when done |
| 99.5% success rate SLA | You hope | ❌ | ✅ |

### 4. Unit economics

If your scraping volume is steady, the managed service is usually cheaper than self-hosting:

| Scenario | Self-hosted (this repo + proxies) | Managed ($0.50/1k) |
|---|---|---|
| 10k products/mo | ~$30 residential proxies + your time | **$5** |
| 100k products/mo | ~$200 residential proxies + ongoing eng maintenance | **$50** |
| 1M products/mo | ~$1,200 residential + ~$1,500/mo eng maintenance | **$500** |

(Proxy estimates assume Bright Data or Oxylabs mid-tier residential pricing, 500KB avg page.)

### 5. Benchmark (our managed service, live 2026-04)

| Metric | Ours | ScrapingBee $49 tier | ScraperAPI $49 tier |
|---|---|---|---|
| Median latency (product, US) | **~2.6 s** | ~3.3 s | n/a |
| P95 latency | **~6 s** | ~22 s | n/a |
| Price / 1,000 products | **$0.50** | $1.63 | $12.25 |
| Concurrent threads (entry paid) | **50** | 10 | 20 |

Tied on success rate (70% on a 30-query mixed international set), **3–4× faster at P95** than ScrapingBee.

---

## What's in this repo

```
amazon-scraper-api/
├── examples/
│   ├── node/
│   │   └── basic-product.js     # ~40 lines, fetch 1 ASIN, parse with cheerio
│   └── python/
│       └── basic_product.py     # ~40 lines, fetch 1 ASIN, parse with BeautifulSoup
├── docs/
│   └── limitations.md           # honest list of what breaks and when
├── LICENSE                      # MIT
└── README.md                    # you are here
```

## Contributing

PRs welcome for:
- Fixes when Amazon changes something and the examples break
- New example targets (different marketplaces, search variant)
- Proxy integrations (Bright Data snippet, Oxylabs snippet, etc.)

PRs we'll politely decline:
- Adding structured extraction for reviews / variants / A+ content (that's what the managed service is for)
- Bundling a specific paid proxy SDK (bring your own, no vendor lock-in)
- Adding retry orchestration / CAPTCHA handling (again: managed)

## Links

- **Managed service:** https://amazonscraperapi.com
- **Docs:** https://amazonscraperapi.com/docs
- **Free tier signup:** https://app.amazonscraperapi.com — 1,000 free requests, no card required
- **Official Node SDK:** [amazon-scraper-api-sdk](https://www.npmjs.com/package/amazon-scraper-api-sdk)
- **Official Python SDK:** [amazonscraperapi-sdk](https://pypi.org/project/amazonscraperapi-sdk/)
- **Official Go SDK:** [github.com/ChocoData-com/amazon-scraper-api-sdk-go](https://github.com/ChocoData-com/amazon-scraper-api-sdk-go)
- **CLI:** [amazon-scraper-api-cli](https://www.npmjs.com/package/amazon-scraper-api-cli)
- **MCP server for AI clients:** [amazon-scraper-api-mcp](https://www.npmjs.com/package/amazon-scraper-api-mcp)

## License

MIT. Use the code however you want. Attribution appreciated but not required.
