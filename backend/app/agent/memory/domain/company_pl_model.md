# Company P&L Model

## Structure

The company P&L projects monthly financials over up to 60 months, built from total wager volume down to net profit.

## Revenue Calculation

1. **Total Monthly Wagers** → Split into Casino (92%) and Sportsbook (8%)
2. **Casino Wagers** → Split into Providers (50%) and OGs (50%)
3. **Provider Wagers** → Split into Pragmatic/Slots (40%) and Evo/Live (60%)
4. **GGR by Channel**:
   - Provider GGR = Provider wagers x 3% edge (97% RTP)
   - OG GGR = OG wagers x 1% edge (99% RTP)
   - Sportsbook GGR = SB wagers x 8% edge (92% RTP)
5. **Effective GGR Rate**: Blended across all channels = ~2.48% of total wagers

## Cost Waterfall

```
Total GGR
  → minus Provider Ops Costs (tiered, progressive)
    - Pragmatic: 6.5% flat (negotiated)
    - Evo: 7.5% effective (tiered)
    - Sportsbook: 11% base (tiered, EUR-based)
  → minus Acquisition Costs
    - Affiliates: 50% of volume, 30% commission on NGR
    - Referrals: 5% of volume, 22% commission
    - Paid: 40% of volume (no commission, but marketing spend)
    - Brand: 5% of volume (organic)
  → minus Bonuses (phase-dependent % of GGR)
  = Profit Before OPEX
    → minus Fixed OPEX (~$1.05M/month)
  = Profit After OPEX
```

## Fixed Monthly OPEX Breakdown

| Category | Monthly Cost |
|----------|-------------|
| Mainstream Marketing | $210,000 |
| Affiliate Retainer | $192,000 |
| Platform (Elantil) | $95,833 |
| Headcount | $420,000 |
| Tools (Smartico etc) | $35,831 |
| Hosting (AWS) | $10,000 |
| DDoS (Cloudflare) | $10,000 |
| Fraud/AML (Sumsub) | $5,632 |
| Others | $50,000 |
| **Total** | **~$1,045,000** |

## Breakeven Logic

Breakeven month = first month where cumulative profit after OPEX turns positive. At $50M monthly wagers, effective GGR is ~$1.24M/month. After all costs and OPEX, early months are negative. Growth rate and bonus phase transitions determine when (or if) cumulative profit crosses zero.

## Key Sensitivities

- **Wager volume**: Primary driver. Doubling wagers roughly doubles GGR but OPEX is fixed, so profit scales faster
- **Bonus rate**: 29-38% of GGR depending on phase. Reducing bonus % has outsized impact on bottom line
- **Provider costs**: Tiered/progressive rates mean higher volume gets better rates
- **Affiliate commission**: 30% of NGR from 50% of volume. Shifting channel mix toward brand/organic dramatically improves margins
