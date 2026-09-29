---
title: A five-factor asset pricing model
authors:
- Eugene F. Fama
- Kenneth R. French
tags:
- asset-pricing-model
- factor-model
- profitability
source: '[[FiveFactor.pdf]]'
model: qwen3.5:9b
created: 2026-09-29
---

# A five-factor asset pricing model

## Authors
Eugene F. Fama, Kenneth R. French

# A five-factor asset pricing model

## Authors
Eugene F. Fama, Kenneth R. French

## Keywords
Asset pricing model, Factor model, Profitability

## 1. Core Contribution & Objective
Extends the Fama-French three-factor model by adding profitability and investment factors to explain average stock returns, specifically addressing anomalies in small stocks that invest heavily despite low profitability. The core hypothesis is that these new factors capture unexplained return variation, potentially rendering the value factor (HML) redundant.

## 2. Methodology & Framework
Uses monthly excess return data from CRSP and Compustat for NYSE, AMEX, and NASDAQ stocks (share codes 10 or 11) from July 1963 to December 2013. Constructs portfolios sorted by Size, Book-to-Market (B/M), Operating Profitability (OP), and Investment (Inv). Performs time-series regressions of portfolio excess returns on factor returns (Market, SMB, HML, RMW, CMA) and tests model performance using GRS statistics and intercept analysis.

## 3. Key Findings & Data Insights
1. The five-factor model reduces unexplained return variance compared to the three-factor model (Table 5). 2. The value factor (HML) is redundant for describing average returns when profitability and investment factors are included, as its high average return is captured by exposures to RMW and CMA (Section 7). 3. Small stocks with low profitability and high investment remain a major problem, showing negative intercepts not fully explained by the five-factor model (Tables 7, 10, 11). 4. Big stocks with similar characteristics show positive unexplained returns, challenging behavioral explanations focused solely on small stocks.

## 4. Limitations & Future Work
The model still fails to capture low average returns for specific small stock portfolios (low profitability, high investment). Measurement error inflates intercept estimates. Results may be specific to the 1963–2013 sample period. Future research is suggested for pre-1963 data or international markets.

## 5. Terms
- **SMB**: Size factor: Return on a diversified portfolio of small stocks minus the return on a diversified portfolio of big stocks.
- **HML**: Value factor: Difference between returns on portfolios of high book-to-market (value) stocks and low book-to-market (growth) stocks.
- **GRS**: Gibbons-Ross-Shanken statistic: A test used to determine if the intercepts in a regression model are jointly distinguishable from zero.

