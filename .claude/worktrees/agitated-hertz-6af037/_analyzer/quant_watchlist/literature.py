"""
Curated finance literature for the watchlist tool.

Heavier emphasis on the cross-sectional / factor-investing literature that
underpins the QVM+L screening framework, vs. the portfolio_analyzer version
which leaned more on portfolio theory and risk management.
"""

LITERATURE = {
    "factor_investing": {
        "section_title": "Factor Investing & Cross-Sectional Returns",
        "what_it_covers": ("How equity returns can be decomposed into systematic 'factor' "
                            "exposures. The intellectual foundation of the QVM+L scoring "
                            "framework used in this report."),
        "papers": [
            {"cite": "Fama, E. F., & French, K. R. (1993). Common Risk Factors in the Returns on Stocks and Bonds. JFE 33(1), 3–56.",
             "url": "https://doi.org/10.1016/0304-405X(93)90023-5",
             "note": "The three-factor model: market, size (SMB), value (HML)."},
            {"cite": "Carhart, M. (1997). On Persistence in Mutual Fund Performance. JF 52(1), 57–82.",
             "url": "https://doi.org/10.1111/j.1540-6261.1997.tb03808.x",
             "note": "Adds momentum (UMD/Mom) as the fourth canonical factor."},
            {"cite": "Fama, E. F., & French, K. R. (2015). A Five-Factor Asset Pricing Model. JFE 116(1), 1–22.",
             "url": "https://doi.org/10.1016/j.jfineco.2014.10.010",
             "note": "Adds profitability (RMW) and investment (CMA) factors."},
            {"cite": "Asness, C., Frazzini, A., & Pedersen, L. (2019). Quality Minus Junk. Review of Accounting Studies 24(1), 34–112.",
             "url": "https://doi.org/10.1007/s11142-018-9477-8",
             "note": "★ Definitive treatment of the quality factor and its construction."},
            {"cite": "Frazzini, A., & Pedersen, L. (2014). Betting Against Beta. JFE 111(1), 1–25.",
             "url": "https://doi.org/10.1016/j.jfineco.2013.10.005",
             "note": "★ Theoretical and empirical foundation of the low-volatility anomaly."},
            {"cite": "Harvey, C., Liu, Y., & Zhu, H. (2016). …and the Cross-Section of Expected Returns. RFS 29(1), 5–68.",
             "url": "https://doi.org/10.1093/rfs/hhv059",
             "note": "Critical review: most published 'factors' fail proper multiple-testing thresholds."},
        ],
    },
    "momentum": {
        "section_title": "Momentum",
        "what_it_covers": ("The empirical finding that recent winners keep winning over "
                            "3–12 month horizons. One of the most-replicated cross-sectional "
                            "anomalies in finance."),
        "papers": [
            {"cite": "Jegadeesh, N., & Titman, S. (1993). Returns to Buying Winners and Selling Losers. JF 48(1), 65–91.",
             "url": "https://doi.org/10.1111/j.1540-6261.1993.tb04702.x",
             "note": "★ Original 12-1 momentum paper. The basis for the momentum window in this tool."},
            {"cite": "Jegadeesh, N. (1990). Evidence of Predictable Behavior of Security Returns. JF 45(3), 881–898.",
             "url": "https://doi.org/10.1111/j.1540-6261.1990.tb05110.x",
             "note": "Short-term reversal: the 1-month return has the opposite sign — hence the 'skip last month' adjustment."},
            {"cite": "Asness, C., Moskowitz, T., & Pedersen, L. (2013). Value and Momentum Everywhere. JF 68(3), 929–985.",
             "url": "https://doi.org/10.1111/jofi.12021",
             "note": "Momentum and value as universal factors across markets and asset classes."},
        ],
    },
    "value": {
        "section_title": "Value",
        "what_it_covers": ("The persistent excess return earned by stocks with low "
                            "price-to-fundamentals multiples."),
        "papers": [
            {"cite": "Basu, S. (1977). Investment Performance of Common Stocks in Relation to Their P/E Ratios. JF 32(3), 663–682.",
             "url": "https://doi.org/10.1111/j.1540-6261.1977.tb01979.x",
             "note": "First formal documentation of the P/E effect."},
            {"cite": "Fama, E., & French, K. (1992). The Cross-Section of Expected Stock Returns. JF 47(2), 427–465.",
             "url": "https://doi.org/10.1111/j.1540-6261.1992.tb04398.x",
             "note": "Documents value (book/market) as a robust factor; market beta alone is insufficient."},
            {"cite": "Lakonishok, J., Shleifer, A., & Vishny, R. (1994). Contrarian Investment, Extrapolation, and Risk. JF 49(5), 1541–1578.",
             "url": "https://doi.org/10.1111/j.1540-6261.1994.tb04772.x",
             "note": "Behavioral interpretation: value works because investors over-extrapolate growth."},
        ],
    },
    "low_volatility": {
        "section_title": "Low Volatility / Min-Variance",
        "what_it_covers": ("The empirical anomaly that low-volatility stocks have earned "
                            "comparable returns to high-volatility stocks while risking far less. "
                            "Counter to CAPM predictions."),
        "papers": [
            {"cite": "Haugen, R., & Heins, J. (1975). Risk and the Rate of Return on Financial Assets. JFQA 10(5), 775–784.",
             "url": "https://doi.org/10.2307/2330270",
             "note": "Earliest empirical challenge to the risk-return relationship implied by CAPM."},
            {"cite": "Frazzini, A., & Pedersen, L. (2014). Betting Against Beta. JFE 111(1), 1–25.",
             "url": "https://doi.org/10.1016/j.jfineco.2013.10.005",
             "note": "★ Theoretical model: leverage constraints cause investors to overpay for high-beta stocks."},
            {"cite": "Baker, M., Bradley, B., & Wurgler, J. (2011). Benchmarks as Limits to Arbitrage. FAJ 67(1), 40–54.",
             "url": "https://doi.org/10.2469/faj.v67.n1.4",
             "note": "Why the low-vol anomaly persists despite being well-documented."},
        ],
    },
    "portfolio_theory": {
        "section_title": "Portfolio Construction",
        "what_it_covers": ("Theory underlying the efficient frontier and how to combine "
                            "multiple assets into a coherent allocation."),
        "papers": [
            {"cite": "Markowitz, H. (1952). Portfolio Selection. JF 7(1), 77–91.",
             "url": "https://doi.org/10.1111/j.1540-6261.1952.tb01525.x",
             "note": "★ Founding paper of modern portfolio theory."},
            {"cite": "Sharpe, W. (1964). Capital Asset Prices. JF 19(3), 425–442.",
             "url": "https://doi.org/10.1111/j.1540-6261.1964.tb02865.x",
             "note": "CAPM and the capital market line."},
            {"cite": "DeMiguel, V., Garlappi, L., & Uppal, R. (2009). Optimal Versus Naive Diversification. RFS 22(5), 1915–1953.",
             "url": "https://doi.org/10.1093/rfs/hhm075",
             "note": "★ 1/N is hard to beat out-of-sample: estimation error overwhelms optimization gains."},
            {"cite": "Michaud, R. (1989). The Markowitz Optimization Enigma. FAJ 45(1), 31–42.",
             "url": "https://doi.org/10.2469/faj.v45.n1.31",
             "note": "Why mean-variance optimization is fragile in practice."},
        ],
    },
    "performance_evaluation": {
        "section_title": "Performance Evaluation & Statistical Inference",
        "what_it_covers": ("How to honestly evaluate whether a backtest's apparent edge is "
                            "real or due to chance / overfitting."),
        "papers": [
            {"cite": "Sharpe, W. (1966). Mutual Fund Performance. Journal of Business 39(1), 119–138.",
             "url": "https://doi.org/10.1086/294846",
             "note": "Original Sharpe ratio formulation."},
            {"cite": "Lo, A. (2002). The Statistics of Sharpe Ratios. FAJ 58(4), 36–52.",
             "url": "https://doi.org/10.2469/faj.v58.n4.2453",
             "note": "★ Standard errors and significance tests for Sharpe ratios with autocorrelation."},
            {"cite": "Bailey, D., Borwein, J., López de Prado, M., & Zhu, Q. (2014). Pseudo-Mathematics and Financial Charlatanism. Notices of the AMS 61(5), 458–471.",
             "url": "https://doi.org/10.1090/noti1105",
             "note": "Why most published backtests are overfit."},
            {"cite": "Bajgrowicz, P., & Scaillet, O. (2012). Technical Trading Revisited. JFE 106(3), 473–491.",
             "url": "https://doi.org/10.1016/j.jfineco.2012.06.001",
             "note": "Out-of-sample test: technical rules don't survive transaction costs."},
        ],
    },
    "behavioral_finance": {
        "section_title": "Behavioral Finance",
        "what_it_covers": ("Why systematic factor anomalies persist despite being well-known: "
                            "human psychology and institutional constraints prevent full arbitrage."),
        "papers": [
            {"cite": "Kahneman, D., & Tversky, A. (1979). Prospect Theory. Econometrica 47(2), 263–291.",
             "url": "https://doi.org/10.2307/1914185",
             "note": "Foundation of behavioral finance. Loss aversion and reference dependence."},
            {"cite": "Barber, B., & Odean, T. (2000). Trading Is Hazardous to Your Wealth. JF 55(2), 773–806.",
             "url": "https://doi.org/10.1111/0022-1082.00226",
             "note": "Empirical: more trading activity → worse performance for retail investors."},
            {"cite": "Shleifer, A., & Vishny, R. (1997). The Limits of Arbitrage. JF 52(1), 35–55.",
             "url": "https://doi.org/10.1111/j.1540-6261.1997.tb03807.x",
             "note": "Why mispricings can persist even when sophisticated traders see them."},
        ],
    },
}
