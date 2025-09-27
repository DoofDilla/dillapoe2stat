# External API Usage

DillaPoE2Stat integrates two external services:
1. **Path of Exile OAuth + Character API** for authenticated inventory snapshots.
2. **poe.ninja economy endpoints** for valuing loot.

This page documents the endpoints, required headers, and helper functions that touch the network.

## Path of Exile API
All calls live in [`poe_api.py`](../poe_api.py). Requests are made with the `requests` library and use the OAuth 2.0 client credentials grant.

### Authentication flow
```
POST https://www.pathofexile.com/oauth/token
Content-Type: application/x-www-form-urlencoded
User-Agent: DillaPoE2Stat/0.1 (+you@example.com)

grant_type=client_credentials
client_id=<CLIENT_ID>
client_secret=<CLIENT_SECRET>
scope=account:characters account:profile
```
- The response contains `access_token` and `expires_in` fields. We print the expiry for visibility.
- `Config.CLIENT_ID` and `Config.CLIENT_SECRET` come from your Path of Exile developer application.

### Character endpoints
Each request includes the header `Authorization: Bearer <access_token>` plus the same user agent.

| Helper | HTTP call | Notes |
| --- | --- | --- |
| `get_characters(access_token)` | `GET https://api.pathofexile.com/character/poe2` | Returns the character list for the account. |
| `get_character_details(access_token, name)` | `GET https://api.pathofexile.com/character/poe2/<name>` | Uses `urllib.parse.quote` to safely encode character names. |
| `snapshot_inventory(access_token, name)` | n/a (wraps `get_character_details`) | Extracts the `character.inventory` array from the JSON response. |

### Rate limiting and etiquette
- `PoEStatsTracker.rate_limit` enforces the `Config.API_RATE_LIMIT` gap (default 2.5 seconds) before each snapshot.
- All network helpers raise `requests.HTTPError` if the service returns a non-2xx status. Callers should wrap usage in `try/except` if they need custom error reporting.

## poe.ninja API
Economy data is consumed via [`price_check_poe2.py`](../price_check_poe2.py). The module normalises item names, caches results, and performs multiple fallbacks to maximise hit rate.

### Endpoints
```
GET https://poe.ninja/poe2/api/economy/temp/overview
Params: leagueName=<league>, overviewName=<category>
Headers: {"User-Agent": "DillaPoE2Stat/0.1 (+you@example.com)", "Accept": "application/json", "Referer": "https://poe.ninja/"}
```
- The tracker defaults to the league defined in `price_check_poe2.LEAGUE`.
- Categories are derived from the heuristics in `guess_category_from_item` or iterated via `DEFAULT_PROBE` fallback list.

### Request helpers
| Helper | Purpose |
| --- | --- |
| `_fetch_items_once(overview_name, league)` | Single HTTP call to fetch raw rows for a category. Raises on failure. |
| `_fetch_items_with_aliases(category_key, league)` | Tries multiple category aliases until a non-empty response is returned. |
| `fetch_category_prices(category_key, league)` | Cached dictionary of normalised item IDs ➜ chaos values. Seeds “Chaos Orb” with `1.0` in currency view. |
| `exalted_price(league)` | Convenience wrapper that pulls Exalted Orb pricing from the currency overview. |

### Lookup strategy
1. **Manual overrides:** `get_value_for_inventory_item` imports `manual_prices.get_manual_item_price` (if present) to support hand-curated valuations.
2. **Category guess:** `guess_category_from_item` inspects frame type, icon path, and name tokens to pick the best poe.ninja category.
3. **Fallback sweep:** If guessing fails, `DEFAULT_PROBE` categories are tested sequentially.
4. **Value aggregation:** `valuate_items_raw` groups items by name, multiplies stack sizes, and returns both chaos and exalt totals. Exalt conversion divides chaos totals by the cached exalted price.

### Error handling and caching
- HTTP responses are cached via `functools.lru_cache` on `fetch_category_prices` and `exalted_price` to reduce API load.
- If a lookup returns `None`, caller-side logic (e.g., `DisplayManager`) will show the item with `-` or omit it in normal mode.
- Manual price lookups catch and log any import errors so the tracker keeps running even if `manual_prices.py` is absent.

## Implementation checklist
When adding new networked features:
- Reuse the `rate_limit` guard before calling `poe_api` helpers.
- Provide a descriptive `User-Agent` string (follow Path of Exile API guidelines).
- Update `Module Reference` and this page to describe new endpoints or heuristics.
- Consider where caching is appropriate to avoid repeated calls mid-session.
