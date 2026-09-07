# Hints

- The `Exchange` field in `index_info` contains full exchange names, such as
  `Tokyo Stock Exchange` and `New York Stock Exchange`. The `Index` field in
  `index_trade` contains abbreviated index symbols, such as `N225`, `HSI`, and
  `000001.SS`. These fields refer to related market entities but do not form a
  directly joinable key. For example, `Tokyo Stock Exchange` corresponds to
  `N225` (Nikkei 225), and `Hong Kong Stock Exchange` corresponds to `HSI`
  (Hang Seng Index).
- The region of each stock exchange is not explicitly provided. Infer it using
  geographic knowledge. For example, `N225` belongs to Asia because it tracks
  the Tokyo Stock Exchange in Japan.
- An up day is a trading day where the closing price is higher than the opening
  price. A down day is a trading day where the closing price is lower than the
  opening price.
- Average intraday volatility is the mean of `(High - Low) / Open` over the
  requested period.
