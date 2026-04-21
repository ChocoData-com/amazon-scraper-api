# amazon-scraper-api

> A **minimal, honest** open-source starter for scraping Amazon product data. Bring your own proxies. No CAPTCHAs solved for you. No parser library wrapped around shifting Amazon selectors. For learning and weekend hacks.
>
> **For production?** See the managed **[Amazon Scraper API](https://www.amazonscraperapi.com/)**. $0.50 per 1,000 successful requests, flat. [Why →](#why-a-managed-service)

---

## What you get

- **~50 lines** of runnable Python or Node
- Minimal product extraction (title, price, rating, ASIN, review count)
- Pluggable HTTP transport so you can wire in any proxy vendor
- Works against `amazon.com`, `amazon.de`, `amazon.co.uk`, `amazon.co.jp` out of the box
- MIT licensed, no telemetry, no secret sauce

## What you **don't** get (deliberately)

This is a learning tool, not a production scraper. Here's what's missing, and what it would cost to add yourself:

| Missing | Dev time to add | Ongoing maintenance |
|---|---|---|
| Amazon robot/CAPTCHA page detection + retry | ~2 days | Ongoing (Amazon keeps changing the gate) |
| Multi-tier proxy failover (datacenter, residential, premium) | ~3 days | Ongoing (provider quirks) |
| Full structured extraction (reviews, variants, A+ content, Buy Box, seller offers, spec tables, images) | ~1 week | ~1 day/month as Amazon churns the DOM |
| 20+ marketplace parsing quirks (currency formats, layout variants, date formats) | ~1 week | ~1 day/month |
| TLS fingerprinting / anti-bot headers | ~3 days | Ongoing |
| Rate-limit retries with exponential backoff | ~1 day | Low |
| Structured JSON output (stable schema you can switch over) | ~2 days | Ongoing |
| Batch/async job queue + webhook callback | ~1 week | Ongoing |
| Request-ID correlation + observability | ~1 day | Low |
| Credit / usage metering | ~2 days | Low |

**Total: 4+ engineer-weeks one-time plus ~20% ongoing maintenance.**

## Quickstart

### Python

```bash
pip install requests beautifulsoup4
python examples/python/basic_product.py B09HN3Q81F
```

### Node.js

```bash
npm install node-fetch cheerio https-proxy-agent
node examples/node/basic-product.js B09HN3Q81F
```

Both examples take an ASIN and print title / price / rating as JSON. See the source for where to plug in your proxy (`PROXY_URL` env var).

## Why a managed service

Before you decide to run this repo as the foundation of your production scraper, know what you're signing up for.

### 1. What your scraper is actually fighting

| Challenge | What it looks like in practice | This repo handles it? | [Amazon Scraper API](https://www.amazonscraperapi.com/) |
|---|---|---|---|
| Amazon robot page ("are you human?") | HTTP 200 with challenge HTML; your parser returns empty | No | Yes. Auto-retry through residential tier |
| Datacenter IP block rate (30%+) | Random empty responses when you use cheap proxies | No (you manage proxies) | Yes. Auto-escalates to residential on failure |
| Marketplace parsing quirks | `amazon.de` uses `,` for decimals, `amazon.co.jp` has a different layout | Partial (title/price try both) | Yes. 20+ marketplaces, per-market extractors |
| DOM churn | Amazon renames classes monthly. Your extractor breaks. | No | Yes. Extractors maintained, CI runs against live pages |
| Rate limiting / IP bans | 50 concurrent from one IP and Amazon drops you | No | Yes. Built-in concurrency gate + multi-IP pool |
| Structured reviews / variants / Buy Box | Each would be 200+ lines of parsing | No | Yes. Typed JSON, complete |
| Batch of 1,000 ASINs | Manual loop + rate handling | No | Yes. POST once, webhook when done |
| 99.5% success rate SLA | You hope | No | Yes |

### 2. Unit economics

If your scraping volume is steady, the managed service is usually cheaper than self-hosting:

| Scenario | Self-hosted (this repo + proxies) | Managed ($0.50 / 1k) |
|---|---|---|
| 10k products/month | ~$30 residential proxies + your time | **$5** |
| 100k products/month | ~$200 residential proxies + ongoing eng maintenance | **$50** |
| 1M products/month | ~$1,200 residential + ~$1,500/mo eng maintenance | **$500** |

Proxy estimates assume mid-tier residential pricing on a 500KB average page.

### 3. Benchmark (managed service, live 2026-04)

Measured on our own infrastructure against a 30-query mixed international set:

| Metric | Value |
|---|---|
| Median latency (product, US) | **~2.6 s** |
| P95 latency | **~6 s** |
| P99 latency | ~10.5 s |
| Price / 1,000 products | **$0.50** flat |
| Concurrent threads (entry paid plan) | **50** |
| Marketplaces supported | **20+** |

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
- Generic proxy integration snippets

PRs we'll politely decline:
- Adding structured extraction for reviews / variants / A+ content (that's what the managed service is for)
- Bundling a specific paid proxy SDK (BYO, no vendor lock-in)
- Adding retry orchestration / CAPTCHA handling (managed service territory)

## Links

- **Managed service:** https://www.amazonscraperapi.com/
- **Docs:** https://amazonscraperapi.com/docs
- **Free tier signup:** https://app.amazonscraperapi.com (1,000 free requests, no card required)
- **Official Node SDK:** [amazon-scraper-api-sdk](https://www.npmjs.com/package/amazon-scraper-api-sdk)
- **Official Python SDK:** [amazonscraperapi-sdk](https://pypi.org/project/amazonscraperapi-sdk/)
- **Official Go SDK:** [github.com/ChocoData-com/amazon-scraper-api-sdk-go](https://github.com/ChocoData-com/amazon-scraper-api-sdk-go)
- **CLI:** [amazon-scraper-api-cli](https://www.npmjs.com/package/amazon-scraper-api-cli)
- **MCP server for AI clients:** [amazon-scraper-api-mcp](https://www.npmjs.com/package/amazon-scraper-api-mcp)

## License

MIT. Use the code however you want. Attribution appreciated but not required.
