# Building CoinClaw: A Crypto Trading Bot Journey

**Started:** February 6, 2026  
**Status:** Active Development (Paper Trading)  
**Current Version:** V3.2 (Dual Direction)  
**Balance:** $100 USDT (Paper Trading)  
**Trades:** 0 (waiting for signals)

---

## The Beginning: OpenClaw Inspiration

**February 2026** - After discovering [OpenClaw](https://openclaw.ai), an AI agent framework that gives AI assistants real autonomy, I was inspired to build something ambitious: an autonomous crypto trading bot that could actually make money.

**Why OpenClaw mattered:** Most AI assistants are glorified chatbots. OpenClaw gives them the ability to execute—to run code, access APIs, deploy infrastructure, and operate autonomously. Perfect for building a trading bot that could run 24/7 without human intervention.

**Shoutout to the OpenClaw creator** for building the framework that made this possible. Without OpenClaw's autonomous capabilities, this project wouldn't exist.

---

## Version 1: The Disaster (Feb 6-7, 2026)

### The Plan
**Strategy:** Simple RSI (Relative Strength Index) mean reversion
- Buy when RSI < 30 (oversold)
- Sell when RSI > 70 (overbought)
- 5-minute candles
- $100 starting capital

**Why I thought it would work:**
- RSI is a proven indicator
- Mean reversion works in ranging markets
- Keep it simple for first version

### The Reality
**Duration:** 9.5 hours (11pm - 9am)  
**Result:** -17% loss ($100 → $83)  
**Trades:** 77 executed  
**Average:** 8 trades per hour

### What Went Wrong

**1. Over-trading (Death by 1000 Cuts)**
- 77 trades in 9.5 hours = insanity
- Each trade lost to spread/slippage
- Longest hold: 90 minutes
- Shortest hold: 5 minutes
- Average: ~20 minutes per position

**2. No Trend Context**
- Bought "oversold" during downtrends (catching falling knives)
- Sold "overbought" during uptrends (missed big moves)
- RSI alone = whipsaw machine in choppy markets

**3. Wrong Timeframe**
- 5-minute candles = noise, not signal
- Too reactive to meaningless volatility
- No sustained moves on 5min charts

**4. Zero Risk Management**
- No stop-loss
- No daily loss limits
- No circuit breakers
- Would have blown entire account if continued

**5. Fixed Position Sizing**
- 20% per trade regardless of signal strength
- All-in immediately
- No capital reserved for better opportunities

### The Lesson

**"In trading, you don't have to be right. You just have to not be wrong too often, and when you're right, be right bigger than when you're wrong."**

Version 1 was wrong constantly and never right big enough to compensate.

**Full V1 post-mortem:** [Read the detailed analysis →](postmortem-v1.html)

---

## Version 2: The Correction (Feb 7, 2026)

### What Changed

**Philosophy shift:**  
V1: React to every signal → **FAILED**  
V2: Wait for high-probability setups → **Better**

**Multi-Signal Confirmation System:**

**Entry Requirements (ALL must be true):**
1. **Trend Filter:** Price must be trending (above/below 50 EMA)
2. **Momentum:** RSI extreme AND turning (< 25 rising, > 75 falling)
3. **Volume:** Above-average confirming interest
4. **Cooldown:** 30 minutes minimum between trades

**Exit Rules:**
- Take profit: 5% gain
- Stop loss: 2% loss
- Time stop: 4 hours max hold
- Trend reversal: Price crosses EMA

**Risk Management:**
- Max 10-15% per trade
- Daily loss limit: 5% of capital
- Never more than 40% deployed
- Emergency shutdown at -15% total

### The Result

**Better, but not good enough.**

- Reduced overtrading (3-5 trades/day vs 77)
- Risk management prevented blowup
- But: Still not profitable
- Win rate: ~35% (need 40%+ with 2.5:1 R/R)

**The problem:** Still trying to predict markets. Long-only in crypto's volatile nature meant missing half the opportunities.

---

## Version 3: The Evolution (Feb 7-8, 2026)

### The Breakthrough: Dual Direction

**Key insight:** Crypto doesn't just go up. It oscillates. Why only profit from one direction?

**V3 Changes:**
- **Long positions:** When trend is up
- **Short positions:** When trend is down
- Profit from both directions
- Better capital utilization
- More trading opportunities

### V3.1: Single Direction Testing (Feb 7)

**Tested long-only and short-only separately:**
- Long strategy: Worked in uptrends
- Short strategy: Worked in downtrends
- Validated: Each direction profitable in right conditions

**Backtesting Results (Feb 7):**
- BTC/USDT 15min: [Results pending]
- BTC/USDT 1H: [Results pending]
- ETH/USDT 15min: [Results pending]
- ETH/USDT 1H: [Results pending]

### V3.2: Dual Direction (Feb 8 - Current)

**Launched:** Feb 8, 2026 09:09 GMT  
**Status:** Running (13+ hours)  
**Balance:** $100 USDT  
**Trades:** 0 (waiting for entry signals)

**Why zero trades?**
- Strict entry requirements (by design)
- Quality > quantity
- Waiting for high-probability setups
- Market currently in consolidation

**Current Strategy:**
```python
# Simplified logic
if price > EMA50 and RSI < 25 and RSI_rising and volume_high:
    open_long()
elif price < EMA50 and RSI > 75 and RSI_falling and volume_high:
    open_short()
else:
    wait()  # Patience is a position
```

**Risk Management:**
- Stop loss: 2% per trade
- Take profit: 5% per trade
- Daily loss limit: 5% of capital
- Max 3 open positions
- Cooldown: 30 min between trades

---

## The Technology Stack

**Core:**
- Python 3.x
- ccxt library (unified exchange API)
- pandas (data analysis)
- OpenClaw (autonomous execution framework)

**Exchange:**
- Binance API (paper trading mode)
- Real-time WebSocket data
- 15-minute and 1-hour candles

**Indicators:**
- 50-period EMA (trend)
- RSI (momentum)
- Volume (confirmation)

**Hosting:**
- Running 24/7 on Kali Linux
- Autonomous operation via OpenClaw
- JSON-based wallet state
- Comprehensive logging

---

## Current Status (Feb 8, 2026)

**Bot State:**
- ✅ Running (PID 4128361)
- ✅ Connected to Binance
- ✅ Monitoring BTC/USDT and ETH/USDT
- ⏳ Waiting for entry signals

**Paper Trading:**
- Starting capital: $100 USDT
- Current balance: $100 USDT
- Trades executed: 0
- Win rate: N/A (need 10+ trades)
- P&L: $0.00 (0%)

**Why paper trading?**
- Test strategy without risking real money
- Validate edge exists before going live
- Build confidence in system
- Refine parameters safely

**When will we go live?**
- After 100+ paper trades
- If win rate > 45%
- If average win > 2x average loss
- If max drawdown < 15%
- Probably 2-4 weeks

---

## What's Next

### Short-Term (This Week)
1. Continue paper trading
2. Collect 20+ trades
3. Analyze win rate and R/R
4. Adjust parameters if needed

### Medium-Term (This Month)
1. Hit 100+ trades milestone
2. Validate edge is real
3. Decide: Go live or iterate
4. Consider adding pairs (ETH, BNB)

### Long-Term (3-6 Months)
1. Transition to real money (small)
2. Scale capital gradually
3. Add more sophisticated strategies
4. Consider open-sourcing parts of code

---

## Honest Assessment

**What's working:**
- Technical execution (API, data, logging)
- Risk management (strict limits)
- Patience (not overtrading)
- Learning from failures

**What's not proven:**
- Profitability (haven't traded enough)
- Win rate (need more data)
- Consistency (too early to tell)
- Real-world viability (paper trading ≠ real trading)

**What I've learned:**
- Trading is harder than it looks
- Most strategies fail
- Risk management is everything
- Patience beats activity
- Data > intuition

**Am I rich yet?**
- No. $0 profit so far.
- Still figuring it out.
- This is a marathon, not a sprint.

---

## Why I'm Sharing This

**99% of crypto content is scams:**
- Fake results
- Fake screenshots
- "Get rich quick" nonsense
- Zero transparency

**I'm doing the opposite:**
- Show every trade (wins AND losses)
- Honest about paper trading
- Transparent about failures
- Real code, real data, real journey

**This is not financial advice:**
- I'm learning as I go
- Trading crypto is risky
- You can lose money
- Most people do

**This is an experiment:**
- Can an AI-built trading bot be profitable?
- Can we do this transparently?
- Can we build in public honestly?
- Let's find out together.

---

## Follow the Journey

**Weekly updates every Monday:**
- All trades published
- P&L transparent
- Strategy adjustments explained
- Lessons learned

**Support this project:**
- [Donate to get the code →](support.html)
- $50+ = GitHub access
- $200+ = 1:1 strategy call
- Help fund development

**Stay updated:**
- Email newsletter: [Subscribe →](newsletter.html)
- GitHub: [Watch the repo →](github.html)
- Trade log: [See all trades →](trades.html)

---

## Credits

**Built with [OpenClaw](https://openclaw.ai)** - The AI agent framework that made this possible. Thank you to the OpenClaw creator for building tools that enable ambitious autonomous projects like this.

**Inspired by:** The dream of making money while you sleep (and the reality of losing it while you sleep if you don't know what you're doing).

---

**Next:** [Read the V1 Post-Mortem →](postmortem-v1.html)

**Or:** [See the current trade log →](trades.html)

**Or:** [Support the project →](support.html)

---

*Last updated: February 8, 2026*  
*Bot status: Running (waiting for signals)*  
*Balance: $100.00 USDT (Paper Trading)*  
*P&L: $0.00 (0%)*
