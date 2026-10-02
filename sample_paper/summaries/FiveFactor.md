---
title: A five-factor asset pricing model
authors:
- Eugene F. Fama
- Kenneth R. French
tags:
- asset-pricing
- factor-model
- five-factor-model
source: '[[FiveFactor.pdf]]'
model: qwen3.5:9b
created: 2026-10-01
---

# A five-factor asset pricing model

## Authors
Eugene F. Fama, Kenneth R. French

## Keywords
Asset pricing, Factor model, Five-factor model

## Short Title
Five-Factor Asset Pricing Model

## Abstract
This paper introduces a five-factor asset pricing model that extends the Fama-French three-factor model by incorporating profitability and investment factors. Using US stock data from 1963 to 2013, the authors demonstrate that the five-factor model explains average returns better than the three-factor model, particularly for portfolios with strong profitability and investment tilts. However, the model still struggles to explain low average returns on small stocks that invest heavily despite low profitability. The study also finds that the value factor (HML) becomes redundant when profitability and investment factors are included.

## 1. Core Contribution & Objective
The paper solves the problem of unexplained variation in average stock returns related to profitability and investment patterns left by the three-factor model. The core hypothesis is that adding profitability (RMW) and investment (CMA) factors improves model performance, potentially rendering the value factor (HML) redundant for describing average returns.

## 2. Methodology & Framework
The study uses monthly excess returns on portfolios formed by sorting stocks on Size, Book-to-Market (B/M), Operating Profitability (OP), and Investment (Inv). The sample includes NYSE, AMEX, and NASDAQ stocks from July 1963 to December 2013. Three sets of factor definitions are tested: independent sorts (2&3), median-based sorts (2&2), and joint control sorts (2&2&2&2). Model performance is evaluated using GRS tests and regression intercepts/slopes.

## 3. Key Findings & Data Insights
1. The five-factor model produces lower GRS statistics and smaller average absolute intercepts than the three-factor model across all portfolio sorts (Table 5).
2. HML becomes redundant in the five-factor model, as its high average return is absorbed by exposures to RMW and CMA (Table 6).
3. Small stocks with low profitability and high investment exhibit significant negative intercepts, representing the main remaining anomaly (Tables 7-11).
4. The value premium is larger for small stocks than big stocks, but controls for profitability and investment reduce this spread.

## 4. Limitations & Future Work
All models are rejected by the GRS test, indicating they are incomplete descriptions of expected returns. Measurement error inflates intercept estimates. The model's failure to capture low returns on small stocks with high investment remains a significant issue. The redundancy of HML might be specific to the 1963-2013 US sample.

## 5. Terms
- **SMB**: Size factor, defined as the return difference between small and big stock portfolios.
- **HML**: Value factor, defined as the return difference between high and low book-to-market equity portfolios.
- **RMW**: Profitability factor, defined as the return difference between robust and weak operating profitability portfolios.

