#!/usr/bin/env node
/**
 * Minimal Amazon product scraper — Node.js version.
 *
 * WHAT THIS DOES
 *   Fetches the Amazon product detail page for a given ASIN and
 *   extracts title, price, rating, and ASIN. That's it.
 *
 * WHAT THIS DOESN'T DO (read the repo README for the full list)
 *   - Handle Amazon's robot page / CAPTCHA
 *   - Rotate proxies on failure
 *   - Extract reviews, variants, images, Buy Box, seller offers
 *   - Handle marketplace quirks beyond the three domains below
 *   - Retry with exponential backoff
 *
 * Usage:
 *   node basic-product.js <ASIN> [domain]
 *   node basic-product.js B09HN3Q81F com
 *   node basic-product.js B000ALVUM6 de
 *
 * Dependencies: node-fetch, cheerio
 *   npm install node-fetch cheerio
 *
 * BYO proxy: see PROXY_URL env var below.
 */
import fetch from 'node-fetch';
import { load } from 'cheerio';
import { HttpsProxyAgent } from 'https-proxy-agent';

const asin = process.argv[2];
const domain = process.argv[3] || 'com';

if (!asin) {
  console.error('Usage: basic-product.js <ASIN> [domain]');
  process.exit(1);
}

// Plug in any HTTP/HTTPS proxy URL via the PROXY_URL env var.
// Examples:
//   export PROXY_URL=http://user:pass@gate.provider.com:8000
//   export PROXY_URL=http://user:pass_country-US@rp.provider.com:1000
// If unset, requests go direct — they will be blocked on ~30% of attempts
// from a datacenter IP. This is why you need a proxy.
const proxyUrl = process.env.PROXY_URL;
const agent = proxyUrl ? new HttpsProxyAgent(proxyUrl) : undefined;

const url = `https://www.amazon.${domain}/dp/${asin}`;
const res = await fetch(url, {
  agent,
  // Anything more realistic than Node's default UA helps — a little.
  headers: {
    'User-Agent':
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
    'Accept-Language': 'en-US,en;q=0.9',
  },
});

if (!res.ok) {
  console.error(`error: HTTP ${res.status} — Amazon likely blocked us. Try a different proxy, or use the managed API at https://amazonscraperapi.com`);
  process.exit(1);
}

const html = await res.text();
const $ = load(html);

// Cheap signal that Amazon served a robot page instead of the product.
if ($('#captchacharacters').length || html.includes('Enter the characters you see below')) {
  console.error('error: Amazon showed a robot check. This scraper does not solve it. Use a residential proxy or the managed API.');
  process.exit(1);
}

// These selectors are correct as of 2026-04 but Amazon rewrites them often.
// If any return empty, don't be surprised — that's the whole point of the README.
const title = $('#productTitle').text().trim();
const priceWhole = $('.a-price .a-price-whole').first().text().replace(/[^0-9]/g, '');
const priceFraction = $('.a-price .a-price-fraction').first().text().replace(/[^0-9]/g, '');
const price = priceWhole ? parseFloat(`${priceWhole}.${priceFraction || '00'}`) : null;
const ratingText = $('#acrPopover').attr('title') || $('.a-icon-star .a-icon-alt').first().text();
const rating = ratingText ? parseFloat(ratingText.match(/([0-9.]+)/)?.[1]) : null;
const reviewCount = parseInt($('#acrCustomerReviewText').text().replace(/[^0-9]/g, ''), 10) || null;

const result = { asin, domain, url, title, price, rating, reviewCount };

if (!title) {
  console.error('warning: extraction returned no title. Amazon may have changed selectors or served a stripped page.');
  console.error('for the structured, maintained version: https://amazonscraperapi.com');
}

console.log(JSON.stringify(result, null, 2));
