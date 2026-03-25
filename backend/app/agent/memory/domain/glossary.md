# Casino Economics Glossary

## Core Metrics

- **Wager Volume (Handle)**: Total amount wagered by players. Nominal volume is raw wagers; weighted volume adjusts by game edge.
- **GGR (Gross Gaming Revenue)**: Total wagers minus payouts. GGR = Wager Volume x House Edge. This is the casino's top-line revenue before any costs.
- **NGR (Net Gaming Revenue)**: GGR minus operational costs, bonuses, and affiliate commissions. This is the actual revenue the casino keeps.
- **RTP (Return to Player)**: The percentage of wagers returned to players as winnings. A 97% RTP means the house keeps 3%.
- **House Edge**: 1 - RTP. The mathematical advantage the casino holds on each wager. Varies by game type.
- **Hold %**: The actual percentage of wagers retained by the casino. In practice, hold % can differ from theoretical house edge due to variance and player behavior.

## Wager Mix Categories

- **Casino 99%+**: High-RTP games (e.g., blackjack, baccarat). Low edge (~1%), attracts VIP volume.
- **Casino 97.5-99%**: Mid-RTP slots and table games. Moderate edge (~1.75%).
- **Casino 97.5%**: Standard slots. Edge around 2.5%.
- **Casino sub-97.5%**: Higher-edge games. Edge ~5.25%.
- **Sportsbook**: Sports betting. Edge ~7% (RTP ~93%).

## Adjustment Factor

The adjustment factor converts nominal wagers to weighted (effective) wagers. It equals `edge / max_edge_in_mix`. Higher-edge games have higher adjustment factors, reflecting their greater revenue contribution per dollar wagered.

## Revenue Waterfall

```
Wager Volume
  → GGR (Volume x Effective Edge)
    → minus Casino Ops (% of casino GGR)
    → minus Sportsbook Ops (% of SB GGR)
    = NGR Before Promos
      → minus Affiliate Commission (% of NGR)
      = NGR After Affiliate
        → minus Bonuses (level-up, reload, weekly, monthly, lossback)
        = NGR After Promos (Net Profit)
```
