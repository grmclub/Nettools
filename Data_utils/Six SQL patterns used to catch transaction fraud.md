Six SQL patterns I use to catch transaction fraud

[analytics.fixelsmith.com](/)

[Home](/) [RSS](/rss.xml) [fixelsmith.com](https://fixelsmith.com)

# Six SQL patterns I use to catch transaction fraud

May 12, 2026

**Quick disclaimer:** I do data work on a program-integrity team. Examples below use generic transaction tables and made-up scenarios. Nothing here comes from anything I’ve actually worked on or seen. Views are mine, not my employer’s.

- - -

Fraud detection in transaction data is mostly SQL. Not machine learning, not graph databases, not whatever Gartner is hyping this year. SQL, run against the right tables, with the right joins, looking for the right shapes.

I work mostly with government-funded benefit programs, but the patterns below port over to anything with a transactions table: credit cards, healthcare claims, e-commerce, point-of-sale. If money moves and gets logged, these queries will find weird things in the log.

Six patterns. Roughly in the order I’d build them out on a new dataset.

## 1\. Velocity

The simplest one. Someone with a stolen card wants to drain it before the holder notices. So they hit the card fast.

```
SELECT
  cardholder_id,
  date_trunc('hour', timestamp) AS hour_bucket,
  count(*) AS tx_count,
  min(timestamp) AS first_tx,
  max(timestamp) AS last_tx
FROM transactions
WHERE timestamp >= current_date - INTERVAL '30 days'
GROUP BY 1, 2
HAVING count(*) > 10;
```

Tune two knobs: the window size and the count threshold. I usually run a 1-minute, 5-minute, and 1-hour version in parallel and compare. Different fraud shows up at different scales — a card-testing ring hits a server in seconds; a benefits-trafficking ring might take an afternoon.

A few cardholders will legitimately blow past the threshold. Route operators servicing vending machines. People reloading prepaid cards in bulk. Your false positives. Worth keeping a whitelist after the first pass.

For sliding-window velocity, this is the form I use:

```
SELECT
  cardholder_id,
  timestamp,
  count(*) OVER (
    PARTITION BY cardholder_id
    ORDER BY timestamp
    RANGE BETWEEN INTERVAL '5 minutes' PRECEDING AND CURRENT ROW
  ) AS tx_in_last_5min
FROM transactions
QUALIFY tx_in_last_5min >= 5
ORDER BY cardholder_id, timestamp;
```

`QUALIFY` works in Snowflake, BigQuery, Databricks, Teradata. For Postgres you wrap the whole thing in a CTE and filter on the outside. Slight pain, same result.

## 2\. Impossible travel

If a card swipes in Chicago and seven minutes later swipes in Los Angeles, one of those swipes is fake. The card is cloned. This is the most uncontroversial fraud signal you’ll find — there’s almost no legitimate reason a single card is in two distant places in seven minutes.

```
WITH ordered_tx AS (
  SELECT
    cardholder_id,
    timestamp,
    location,
    LAG(timestamp) OVER (PARTITION BY cardholder_id ORDER BY timestamp) AS prev_ts,
    LAG(location)  OVER (PARTITION BY cardholder_id ORDER BY timestamp) AS prev_loc
  FROM transactions
)
SELECT
  cardholder_id,
  prev_ts  AS first_tx,
  timestamp AS second_tx,
  prev_loc  AS first_location,
  location  AS second_location,
  EXTRACT(EPOCH FROM (timestamp - prev_ts)) / 60 AS minutes_apart,
  haversine(prev_loc, location)                  AS miles_apart
FROM ordered_tx
WHERE prev_ts IS NOT NULL
  AND prev_loc <> location
  AND haversine(prev_loc, location)
        / nullif(EXTRACT(EPOCH FROM (timestamp - prev_ts)), 0)
        * 3600 > 600;
```

`haversine` is the great-circle distance function. Most warehouses ship one. If yours doesn’t, it’s about ten lines to write your own.

The 600 mph threshold is rough — commercial jet cruise is around 575, so this is “faster than a plane could possibly do it.” You can tighten it to 100 mph if you want to catch suspiciously-fast ground travel too, but at that threshold you start picking up real airline travelers, kids with parents driving them home from camp, that kind of thing.

A few other shapes in the same family are worth running:

*   Two distant cities, same state, inside 5 minutes. Local cloning rings.
*   Multiple ZIP codes inside an hour. Skimmer rings working a region.
*   Border crossings inside 10 minutes. International rings.

## 3\. Amount anomalies

There are a couple of amounts that show up disproportionately in fraud and almost never in normal use.

```
SELECT cardholder_id, timestamp, amount, merchant_id
FROM transactions
WHERE
  (amount >= 99.50  AND amount < 100.00)
  OR (amount >= 499.50 AND amount < 500.00)
  OR amount IN (1.00, 5.00, 10.00)
ORDER BY cardholder_id, timestamp;
```

What’s happening:

Round dollar amounts at small values — $1.00, $5.00, $10.00 — are almost always card tests. Someone got a card number from a dump and they’re checking if it works before reselling it. Real cardholders almost never buy something for exactly $1.00. Coffee is $4.73, gas is $52.81. The roundness is the signal.

Amounts just below a threshold are different. $99.99 is interesting because at a lot of places, $100 is the line where the cashier is supposed to check ID. $499.99 is interesting because $500 is often a daily ATM cap. Whoever’s doing the transaction knows the rules and is staying under them.

(For benefits transactions specifically, the round-number pattern doesn’t help much. Benefits don’t get card-tested the same way. There the signal is usually duplicate recipients, which is a different post.)

## 4\. Suspicious merchants

When a skimmer compromises a card reader at, say, a gas pump, you don’t get one fraud case. You get dozens. Every card swiped at that pump for the next few weeks is now in someone’s database. So the symptom from the merchant side is: an unusual number of unrelated cards spending more than usual, in a short window.

```
SELECT
  merchant_id,
  date_trunc('hour', timestamp) AS hour_bucket,
  count(DISTINCT cardholder_id) AS unique_cards,
  count(*) AS total_tx,
  sum(amount) AS total_amount
FROM transactions
WHERE timestamp >= current_date - INTERVAL '7 days'
GROUP BY 1, 2
HAVING count(DISTINCT cardholder_id) > 20
  AND sum(amount) > 5000
ORDER BY total_amount DESC;
```

The problem with static thresholds (20 unique cards, $5000) is they don’t account for size. A Costco does that in 90 seconds. A used bookshop, never. So the better version compares each merchant against itself:

```
WITH merchant_hourly AS (
  SELECT
    merchant_id,
    date_trunc('hour', timestamp) AS hour_bucket,
    count(DISTINCT cardholder_id) AS unique_cards
  FROM transactions
  WHERE timestamp >= current_date - INTERVAL '60 days'
  GROUP BY 1, 2
),
with_baseline AS (
  SELECT
    *,
    avg(unique_cards) OVER (
      PARTITION BY merchant_id
      ORDER BY hour_bucket
      ROWS BETWEEN 168 PRECEDING AND 1 PRECEDING
    ) AS rolling_avg_cards
  FROM merchant_hourly
)
SELECT *,
  unique_cards / nullif(rolling_avg_cards, 0) AS spike_ratio
FROM with_baseline
WHERE unique_cards > rolling_avg_cards * 3
ORDER BY spike_ratio DESC;
```

The 168 is the trailing seven days of hourly buckets. I use a week because daily and weekly seasonality matters — Tuesday 2pm at a coffee shop is not the same baseline as Saturday 9am at the same shop. A week catches both cycles.

Three times normal is where I start. It’s loose enough not to drown you in alerts but tight enough to flag the actually weird hours.

## 5\. Off-hours

Most people are creatures of habit when they spend money. A nine-to-fiver doesn’t suddenly start buying gas at 3am. If their card does, it’s either being used by someone else or they’re traveling — and travel produces other signals you can check.

```
WITH cardholder_hour_pattern AS (
  SELECT
    cardholder_id,
    EXTRACT(HOUR FROM timestamp) AS hour_of_day,
    count(*) AS tx_count
  FROM transactions
  WHERE timestamp >= current_date - INTERVAL '90 days'
  GROUP BY 1, 2
),
cardholder_normal AS (
  SELECT
    cardholder_id,
    min(hour_of_day) FILTER (WHERE tx_count >= 2) AS earliest_hour,
    max(hour_of_day) FILTER (WHERE tx_count >= 2) AS latest_hour
  FROM cardholder_hour_pattern
  GROUP BY 1
)
SELECT t.cardholder_id, t.timestamp, t.amount, t.merchant_id
FROM transactions t
JOIN cardholder_normal cn USING (cardholder_id)
WHERE EXTRACT(HOUR FROM t.timestamp) NOT BETWEEN cn.earliest_hour AND cn.latest_hour
ORDER BY t.timestamp DESC;
```

The “two or more in that hour” filter on the inner query is doing important work. Without it, one stray late-night gas station purchase three months ago becomes part of the cardholder’s “normal” hours, and you never flag them again. Requiring at least two purchases in a given hour, in 90 days, sets the bar at “actually a habit” instead of “happened once.”

Drawback: this doesn’t work until you have history. New accounts have no baseline. For those, you fall back to global hour patterns or just skip this pattern entirely until they’ve been around for a couple months.

## 6\. Window functions for chained signals

This one isn’t really a pattern. It’s a setup that makes the other five patterns composable.

```
SELECT
  cardholder_id,
  timestamp,
  amount,
  merchant_id,

  timestamp - LAG(timestamp) OVER w AS time_since_last,

  CASE WHEN merchant_id <> LAG(merchant_id) OVER w
       THEN 'changed' ELSE 'same' END AS merchant_change,

  sum(amount) OVER (
    PARTITION BY cardholder_id
    ORDER BY timestamp
    RANGE BETWEEN INTERVAL '24 hours' PRECEDING AND CURRENT ROW
  ) AS running_24h_total,

  ROW_NUMBER() OVER (
    PARTITION BY cardholder_id, date(timestamp)
    ORDER BY timestamp
  ) AS tx_of_day

FROM transactions
WINDOW w AS (PARTITION BY cardholder_id ORDER BY timestamp)
ORDER BY cardholder_id, timestamp;
```

Once you’ve materialized those columns, fraud rules collapse to filter expressions. Say you’re hunting card-testing rings, where the tell is “lots of small charges, all at different merchants, within minutes of each other.” The rule becomes:

```
SELECT *
FROM tx_with_windows
WHERE tx_of_day >= 5
  AND time_since_last < INTERVAL '60 seconds'
  AND merchant_change = 'changed';
```

Three filters. That’s it.

The reason this matters is that the moment your analysts can express new fraud hypotheses as SQL filters instead of engineering tickets, your iteration loop drops from weeks to hours. You catch more fraud, faster.

## Putting it together

None of these alone is enough. Velocity has false positives (vending operators). Geographic impossibility misses anything inside a single metro. Amount anomalies don’t apply outside of card-test contexts. The off-hours rule needs history.

What works is running them all and scoring each transaction across the signals. A transaction that fails on three or four of them is almost always fraud. A transaction that fails on one might be your grandma being weird with her debit card on vacation.

If you’re brand new to fraud detection, start with pattern 1. It alone will surface a useful amount of fraud and very little legitimate activity, and it’s cheap to run.

If you’ve already got 1 through 5, the place to invest is pattern 6 — those window-function primitives. Every analyst on your team will use them once they exist, and adding the next fraud pattern stops being a project.

## Things I left out

A few things this post doesn’t cover that come up constantly:

NULL handling. Real transaction tables don’t use NULL the way intro SQL books do. A lot of legacy systems use sentinel values like `9999-12-31` for “no end date” or `0001-01-01` for “no start date.” Filtering with `IS NULL` will silently miss those rows. Always check what the convention is in your specific table before writing WHERE clauses that assume NULL.

False positives. Every rule above will flag real cardholders doing weird-but-legitimate things. Your fraud workflow needs human review of flagged cases, with a feedback loop that lets you tune thresholds based on what’s actually fraud and what isn’t. Auto-blocking on a single rule is how you lose customers.

Privacy. If the data has PII, your queries need to comply with your applicable data-use policies. De-identified or sampled data first, production data with authorization second.

Cost. Window functions with big partitions are not cheap. Filter your date range first, then apply the window, not the other way around. I’ve watched a junior analyst burn through a warehouse credit budget by running a `LAG()` across two years of transactions on the entire dataset before adding the WHERE.

- - -

Things I want to write about next, depending on what people ask for:

*   Eight window-function tricks beyond `LAG` and `ROW_NUMBER`
*   Detecting fraud rings, which is the social-graph problem in disguise
*   What goes on a fraud team’s dashboard, and what doesn’t
*   Why your fraud alerts are noisy, and how to actually fix that instead of just raising thresholds

If there’s something specific you want covered, message through [fixelsmith.com](https://fixelsmith.com).

- - -

_Fixel Smith is an experienced Program Integrity Analyst working in public-sector data._


[fixelsmith.com](https://fixelsmith.com)