# A five-factor asset pricing model

## Authors
Eugene F. Fama, Kenneth R. French

## Keywords
Asset pricing model, Factor model, Dividend discount model

## 1. Core Contribution & Objective
Extends the Fama-French three-factor model by adding profitability (RMW) and investment (CMA) factors to better explain average stock returns across size, value, profitability, and investment dimensions. The core hypothesis is that these additional factors capture significant variation in expected returns, potentially rendering the traditional value factor (HML) redundant.

## 2. Methodology & Framework
Uses US stock data from CRSP and Compustat covering July 1963 to December 2013 (606 months). Constructs portfolios based on independent sorts of Size, Book-to-Market (B/M), Operating Profitability (OP), and Investment (Inv). Employs time-series regressions of excess returns against market, size, value, profitability, and investment factors. Compares model performance using GRS statistics, intercepts, and variance ratios across three sets of factor definitions (2 & 3 sorts, 2 & 2 sorts, and 2 & 2 & 2 & 2 sorts).

## 3. Key Findings & Data Insights
1. The five-factor model significantly outperforms the three-factor model in explaining average returns on portfolios formed on profitability and investment (Table 5), reducing unexplained variance to 42-54% compared to 54-68% for the three-factor model. 2. HML becomes redundant; its high average return is absorbed by exposures to RMW and CMA, particularly in the five-factor model (Section 7, Table 6). 3. A persistent anomaly exists: small stocks with low profitability and high investment (negative RMW/CMA slopes) exhibit low average returns that the model fails to fully capture (Abstract, Section 8, Tables 7 & 10). 4. Factor definition sensitivity is low; results are robust across different factor construction methods.

## 4. Limitations & Future Work
The model still leaves a substantial portion of return variance unexplained (approx. 28% for Size-Inv portfolios). Results may be specific to the US sample period (1963-2013) and do not necessarily apply to pre-1963 or international data. Measurement error inflates intercept estimates. The model fails to capture returns of small stocks that invest heavily despite low profitability.

## 5. Terms
- **HML**: High Minus Low: A factor representing the difference between returns on high book-to-market (value) and low book-to-market (growth) portfolios.
- **RMW**: Robust Minus Weak: A factor capturing the difference in returns between firms with robust operating profitability and those with weak profitability.
- **CMA**: Conservative Minus Aggressive: A factor representing the difference in returns between firms with conservative investment (low growth in assets) and aggressive investment (high growth in assets).

