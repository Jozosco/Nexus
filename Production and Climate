# Soybean Oil: Major Production Regions, Top Importers & Climate Data API Feasibility (2020–2025)

**NEXUS Intelligence Report | Climate/Agriculture Module — Step 2**
*Reference: USDA FAS PSD data, April 2026*

***

## Executive Summary

Global soybean oil production is dominated by **China (~19.9 MMT), the United States (~11.6 MMT), Brazil (~10.8 MMT), and Argentina (~8.2 MMT)**, together accounting for over 85% of world output. The top three soybean oil importers — **India, Bangladesh, and Algeria** — are structurally import-dependent, with India alone representing ~28–30% of global soybean oil import volume. Free government-grade APIs exist to collect climate data for most major sub-national production regions, but the depth and granularity of sub-national agricultural statistics APIs varies significantly by country.[^1][^2][^3]

***

## Part 1 — Top 3 Production Regions per Country

### 1.1 China

China's soybean crushing industry is **spatially bifurcated**: domestic soybean *growing* is concentrated in the northeast, while industrial *crushing* (which drives oil production) is concentrated in coastal provinces fed by imported beans.[^4]

**Soybean Growing Provinces (domestic raw material):**

| Rank | Province | Characteristic |
|------|----------|----------------|
| 1 | **Heilongjiang** | ~47% of China's total soybean output; 4.93M ha sown in 2022, yielding 9.54B kg[^5][^6] |
| 2 | **Inner Mongolia** | Second-largest growing province; scale advantage, subsidized planting alongside Heilongjiang[^7][^8] |
| 3 | **Jilin / Liaoning** | Northeast China plain; government-subsidised; limited alternatives vs. corn[^8] |

**Soybean Oil Crushing Provinces (where oil is actually produced):**

| Rank | Province | Characteristic |
|------|----------|----------------|
| 1 | **Shandong** | Largest share of coastal crushing capacity; port-access for imported beans[^4] |
| 2 | **Jiangsu** | Second-largest coastal crushing hub; Yangtze River access[^4] |
| 3 | **Guangdong** | Major southern coastal cluster; deep-water port access for Brazilian/US beans[^4] |

> **Critical structural note:** 85% of China's ~140 MMT annual crush capacity is located in coastal provinces processing *imported* soybeans, not domestic production. Only ~15% is inland. Therefore, for oil production analysis, Shandong/Jiangsu/Guangdong are the correct regions to monitor; for *crop yield* climate risk, Heilongjiang/Inner Mongolia/Jilin are the relevant regions.[^9][^10][^4]

**Sub-national Data Availability (China):**

| Source | Data Type | Granularity | API |
|--------|-----------|-------------|-----|
| National Bureau of Statistics (NBS) | Sown area, yield per ha, annual production | Province-level | Free, no key — `http://data.stats.gov.cn/english/easyquery.htm` |
| USDA FAS GAIN Reports | Crushing volume, crush capacity, policy | Provincial narrative | Free download (GAIN API, no key) |
| CNGOIC (China National Grain & Oils Info Center) | Monthly crush, oil output | National only | **Paid/subscription** |

***

### 1.2 United States

The US soybean belt is concentrated in the Midwest Corn Belt. Crushing (oil production) infrastructure is heavily located in Illinois and Iowa.[^11][^12]

**Top 3 Soybean Producing States:**

| Rank | State | 2024 Production (MMT) | Notes |
|------|-------|----------------------|-------|
| 1 | **Illinois** | 18.7 MMT[^13] | Largest state crusher capacity; ADM, Bunge, Cargill plants |
| 2 | **Iowa** | 16.3 MMT[^13] | Highest crush capacity of any state — >1.3M bu/day[^12] |
| 3 | **Indiana** | 9.3 MMT[^13] | Top 3 together account for >37% of US total production[^11] |

*Minnesota (9.0 MMT) and Nebraska (8.2 MMT) are close 4th/5th. North Dakota is expanding rapidly with crush capacity up from 6% to 47% of state production since 2023.*[^13][^14]

**Sub-national Data Availability (USA):**

| Source | Data Type | Granularity | API |
|--------|-----------|-------------|-----|
| **USDA NASS QuickStats** | Planted/harvested area, yield/bu, production — annual & monthly | State + county level | **Free** — REST API, requires free key: `https://quickstats.nass.usda.gov/api` |
| **USDA ERS** | Sector overviews, crush data | National | Free, no API but open data downloads |
| **EIA** | Soybean oil for biofuel (RFS) | National/regional | Free REST API, key required |

***

### 1.3 Brazil

Brazil's soybean oil production is driven by crushing infrastructure spread across 5 states, with Mato Grosso holding the highest raw soybean volume.[^15][^16]

**Top 3 Soybean Producing & Crushing States:**

| Rank | State | Characteristic |
|------|-------|----------------|
| 1 | **Mato Grosso (MT)** | Highest soybean production volume nationally; average yield ~3.90 MT/ha (2024)[^15]; MapBiomas tracks annual crop area at 30m resolution |
| 2 | **Paraná (PR)** | Major oil extraction state; yield reached 3.66 MT/ha (+16.1% YoY in 2024)[^15]; ~26% of Brazil crushing capacity |
| 3 | **Mato Grosso do Sul (MS)** | 4.7M ha cultivated; 2025/26 crop ~17.7 MMT projected, +26.3% YoY[^17] |

*Other significant states: Goiás (GO), Rio Grande do Sul (RS), and São Paulo (SP). The five states MT, MS, GO, PR, RS together account for ~74.9% of total production.*[^18]

**Sub-national Data Availability (Brazil):**

| Source | Data Type | Granularity | API |
|--------|-----------|-------------|-----|
| **CONAB** | Annual/monthly planted area, production, yield estimates by state/micro-region | State + municipality | **Free** — Open Data portal: `https://portaldeinformacoes.conab.gov.br/` (JSON/CSV download, no formal REST key required) |
| **IBGE (SIDRA)** | Agricultural census, PAM annual crop data | Municipality-level | **Free** REST API: `https://sidra.ibge.gov.br/home/pmc/brasil` |
| **MapBiomas** | Satellite-derived soybean crop area (30m resolution) | Pixel/state/municipality | **Free** via Google Earth Engine (GEE) platform[^19][^20] |
| **ABIOVE** | Monthly crush volume, oil and meal production | National + state | Free PDF reports; no formal API |

***

### 1.4 Argentina

Argentina's soybean oil production is overwhelmingly concentrated along the Paraná River corridor near Rosario, Santa Fe province, where ~80% of national crushing capacity is located.[^21]

**Top 3 Soybean Producing Provinces:**

| Rank | Province | Characteristic |
|------|----------|----------------|
| 1 | **Córdoba** | Top soybean-producing province; 2024/25 first-crop estimate 13.3 MMT[^22]; also hosts 6 oil processing plants |
| 2 | **Santa Fe** | Home to the "Gran Rosario" crush hub (165,800 MT/day capacity); 22 of Argentina's 51 oil processing plants[^23] |
| 3 | **Buenos Aires** | Third-largest producer; southern zones supply southern deepwater ports[^24]; Buenos Aires holds 16 of Argentina's 51 oil plants[^23] |

*La Pampa and Entre Ríos are secondary growing regions. San Lorenzo (Santa Fe) is the single most important processing location — it anchors Argentina's #1 global exporter position for soybean oil.*[^25][^26]

**Sub-national Data Availability (Argentina):**

| Source | Data Type | Granularity | API |
|--------|-----------|-------------|-----|
| **MAGyP (Secretaría de Agricultura)** | Monthly oilseed crush, oil production, meal production | National + some province | **Free** — Datos Abiertos: `https://datos.gob.ar/dataset` (CSV/JSON, no key)[^27] |
| **SIIA (Sistema Integrado de Información Agropecuaria)** | Area sown, production, yield per crop per province | Province-level, annual | **Free** — `https://www.argentina.gob.ar/agricultura/siia` |
| **Bolsa de Cereales de Buenos Aires (BCBA)** | Weekly crop progress, planting %, harvest % | Regional | Free PDF/bulletins; no formal REST API |
| **Rosario Stock Exchange (BCR)** | Weekly crop condition, regional production estimates | Regional (Pampas) | Free bulletins; no REST API |

***

## Part 2 — Top 3 Soybean Oil Importing Countries (2020–2025)

### 2.1 Rankings

Based on USDA FAS PSD data and World Bank WITS trade data, the consistent top 3 soybean oil importers by volume over 2020–2025 are:

| Rank | Country | Avg. Annual Import Vol. | Primary Supplier | Notes |
|------|---------|------------------------|-----------------|-------|
| 🥇 | **India** | ~3.0–3.9 MMT/year | Argentina (~50%), Brazil (~35%) | World's largest importer; ~28–30% of global import volume[^2][^3][^28] |
| 🥈 | **Bangladesh** | ~0.8–1.1 MMT/year | Brazil, Argentina | Strong 5-yr CAGR of +2.41%[^3]; significant FX dependency |
| 🥉 | **Algeria** | ~0.6–0.9 MMT/year | Argentina, Brazil | Domestic crushing expansion is driving soybean imports up (2025/26 soybeans import raised +350,000 MT)[^29] |

*Note: China is classified as a **producer/consumer**, not a net soybean oil importer. China imports raw soybeans and crushes domestically; its soybean oil imports are minor (~3% global share). The EU collectively imports ~623,000 MT but is counted as a bloc.*[^2][^30][^31]

### 2.2 India — 6-Year Import Summary

| Marketing Year | Soybean Oil Imports (MMT) | Key Notes |
|----------------|--------------------------|-----------|
| 2020/21 | ~3.29 MMT | Base period average (Oct–Sep MY)[^28] |
| 2021/22 | ~3.5 MMT | +49% value surge; peak global prices[^32] |
| 2022/23 | ~3.2–3.5 MMT | Value peak at $5.9B; price-driven, not volume[^32] |
| 2023/24 | ~3.0–3.2 MMT | Tight global supply limited imports through Mar 2024[^33] |
| 2024/25 (est.) | ~3.7–5.1 MMT | USDA forecast raised to 3.7 MMT[^33]; SEA reports crude imports soared +116% in Nov 2024–Mar 2025[^34] |
| 2025/26 (fcst.) | ~3.0 MMT | USDA official cut of 300,000 MT on pace-of-trade[^35] |

Argentina emerged as India's dominant supplier with 12.16 lakh tonnes (Nov 2024–Mar 2025) vs 4.51 lakh tonnes in the prior period.[^34]

### 2.3 Bangladesh — 6-Year Import Summary

| Year | Soybean Oil Imports (approx.) | Key Notes |
|------|-------------------------------|-----------|
| 2020/21 | ~0.0 MMT (trace) | Minimal prior to surge[^36] |
| 2021/22 | ~1.1 MMT | Rapid emergence; +59.7% over prior year per FAS[^36] |
| 2022/23 | ~1.0–1.1 MMT | Consolidation; FX pressure from USD strength |
| 2023/24 | ~0.9–1.0 MMT | Economic headwinds[^35] |
| 2024/25 | ~0.9 MMT | Slight recovery per USDA[^35] |
| Trend | 5-yr CAGR: **+2.41%**[^3] | Import share ~8.7% of global volume[^3] |

### 2.4 Algeria — 6-Year Import Summary

| Year | Soybean Oil Imports (approx.) | Key Notes |
|------|-------------------------------|-----------|
| 2020–2022 | ~0.5–0.7 MMT/yr | Steady domestic consumer demand |
| 2022/23 | ~0.69 MMT | +16% YoY[^2] |
| 2023/24 | ~0.7 MMT | Stable; 5-yr CAGR -8.4%[^2] (share basis) |
| 2024/25 | Trend up | Algeria's soybean imports for crushing raised +350,000 MT to 2.05 MMT by USDA for 2025/26[^29], signaling growing domestic crush investment |
| Key driver | Domestic crushing expansion | Shift: importing raw soybeans to crush locally, potentially reducing *oil* imports longer-term |

***

## Part 3 — Climate Data API Feasibility for Production Regions

To complement sub-national production statistics with climate variables (precipitation, temperature, soil moisture, ENSO-linked anomalies), the following free APIs are recommended:

### 3.1 Free Climate APIs — Priority Ranking

| Priority | API | Coverage | Resolution | Key Variables | Auth | Cost |
|----------|-----|----------|------------|---------------|------|------|
| 🥇 | **Open-Meteo Historical Weather API** | Global (ERA5/ERA5-Land) | 0.1°–0.25° (~11–25 km) | Temp, precip, humidity, soil temp/moisture, solar radiation, wind | **No key required** | **Free** (non-commercial)[^37][^38] |
| 🥇 | **NASA POWER API** | Global | 0.5° × 0.625° | Temp, humidity, precip, solar radiation, evapotranspiration — "AG" community optimized | **No key required** | **Free**[^39][^40] |
| 🥈 | **NOAA NCEI CDO** | Global (station data) | Station-level | Daily/monthly temp, precip, degree days | Free key | **Free**[^41] |
| 🥈 | **Copernicus CDS (ERA5)** | Global | 0.25° | Full atmospheric reanalysis: 1940–present; hourly | Free registration | **Free**[^42] |
| 🥉 | **Google Earth Engine (GEE)** | Global | Sub-meter to 25km | ERA5, CHIRPS rainfall, MODIS NDVI, soil data | Free (research) | **Free** for non-commercial[^19] |
| ❌ | **Weatherbit Ag Weather API** | Global | Point | Soil temp/moisture, ET₀ | Key required | **Paid** (Business/Enterprise only)[^43] |

### 3.2 API Coordinate Mapping for Target Regions

The table below provides reference coordinates for querying Open-Meteo and NASA POWER APIs directly by region:

| Country | Region | Approx. Center Lat/Lon | Notes |
|---------|--------|------------------------|-------|
| China | Heilongjiang (grow) | 48.0°N, 128.0°E | Major domestic soybean zone |
| China | Shandong (crush) | 36.5°N, 118.0°E | Largest coastal crushing cluster |
| China | Jiangsu (crush) | 32.5°N, 120.0°E | Yangtze River crushing hub |
| USA | Illinois | 40.0°N, -89.0°W | #1 state production |
| USA | Iowa | 42.0°N, -93.5°W | #1 state crush capacity |
| USA | Indiana | 40.2°N, -86.1°W | #3 state production |
| Brazil | Mato Grosso | -13.0°S, -56.0°W | Top production state |
| Brazil | Paraná | -24.5°S, -51.5°W | Major oil processing state |
| Brazil | Mato Grosso do Sul | -20.0°S, -54.5°W | Significant & growing |
| Argentina | Córdoba | -31.4°S, -64.2°W | #1 growing province |
| Argentina | Santa Fe (Rosario) | -33.0°S, -60.6°W | Crushing hub — 80% national capacity |
| Argentina | Buenos Aires | -36.0°S, -60.0°W | Core Pampas growing zone |

### 3.3 Recommended API Call Architecture

For the NEXUS pipeline, a two-API strategy is recommended:

**Tier 1 — Open-Meteo (primary):** Daily historical data 1940–present, any coordinate, no key, JSON format.
```
https://archive-api.open-meteo.com/v1/archive?
  latitude={LAT}&longitude={LON}
  &start_date=2020-01-01&end_date=2025-12-31
  &daily=temperature_2m_max,temperature_2m_min,precipitation_sum,
         soil_moisture_0_to_7cm,et0_fao_evapotranspiration
  &timezone=auto
```

**Tier 2 — NASA POWER (validation/soil):** Agricultural community, daily, free, no key, covers 1981–present at 0.5° resolution. Optimized for crop modeling with dedicated `AG` community parameters including ET₀, surface soil wetness, and root-zone moisture.
```
https://power.larc.nasa.gov/api/temporal/daily/point?
  parameters=T2M,PRECTOTCORR,RH2M,ALLSKY_SFC_SW_DWN,WS2M
  &community=AG&longitude={LON}&latitude={LAT}
  &start=20200101&end=20251231&format=JSON
```

***

## Anomaly & Alert Flags

| Flag | Indicator | Finding | Signal |
|------|-----------|---------|--------|
| ⚠️ | **Algeria import strategy shift** | USDA raised Algeria soybean *raw* imports +350,000 MT for 2025/26 while soybean oil imports have trended stable/down — suggests domestic crush buildup that could reduce Algeria's soybean oil import dependency medium-term[^29] | Downward import pressure (lagged) |
| ⚠️ | **India surge 2024/25** | India's crude soybean oil imports soared +116% in Nov 2024–Mar 2025 to 19.11 lakh tonnes vs 8.83 lakh tonnes prior period[^34] | Upward price pressure |
| ⚠️ | **China coastal crush dominance** | 85% of China's 140 MMT crush capacity is at coastal ports processing imported beans — meaning climate risk in Heilongjiang has **no direct path** to Chinese oil production; the transmission mechanism is **trade flow**, not domestic yield[^4] | Structural data architecture risk |
| ℹ️ | **Bangladesh/Algeria FX vulnerability** | Both countries are FX-constrained importers; USD-denominated oil prices + local currency weakness historically compress import volumes | Demand downside risk |

***

## Data Gap Summary

| Gap | Description | Workaround |
|-----|-------------|------------|
| China sub-national crush data | CNGOIC monthly crush by province is **subscription-only** | Use USDA GAIN narratives (free) + NBS annual provincial data |
| Argentina province-level oil production | MAGyP publishes national monthly data; **province-level oil production** is not systematically available in open API | Use Santa Fe / Gran Rosario as proxy for 80% of national output |
| Bangladesh sub-annual import data | Bangladesh Tariff Commission does not publish monthly import API | Use USDA FAS PSD (annual MYs) + UN Comtrade (HS 150710 monthly, free) |
| India monthly import timely data | SEA (Solvent Extractors' Association) has timely data but no open API | USDA GAIN reports + UN Comtrade HS 150710 as fallback |

---

## References

1. [Global Soybean Oil Production by Country, 2023](https://www.reportlinker.com/dataset/e6b9258c974da1733b23fbfd5becac5cabc235de) - Global Soybean Oil Production by Country, 2023

2. [Global Soybean Oil Import Share by Country (Thousand Metric Tons), 2023](https://www.reportlinker.com/dataset/b6790e7d7b798a167993836f8339ca996a9c3268) - Global Soybean Oil Import Share by Country (Thousand Metric Tons), 2023

3. [Global Soybean Oil Import Volume Share by Country (Thousand Metric Tons), 2023](https://www.reportlinker.com/dataset/a807437dedaf6605808940bca27759f2f754082c) - Global Soybean Oil Import Volume Share by Country (Thousand Metric Tons), 2023

4. [China's relentless soybean crushing build-out drives imports](http://dimsums.blogspot.com/2024/12/chinas-relentless-soybean-crushing.html) - The largest concentration of soybean crushing facilities are in the provinces of Shandong, Jiangsu, ...

5. [China's largest soybean-producing province sets new records](http://english.www.gov.cn/news/topnews/202212/18/content_WS639e757fc6d0a757729e48f1.html) - Heilongjiang yielded 9.54 billion kilograms of soybeans this year, up 32.6 percent year on year and ...

6. [China food security: top soybean region Heilongjiang unveils plan to ...](https://www.scmp.com/economy/china-economy/article/3161977/china-food-security-top-soybean-region-heilongjiang-unveils) - China's northeastern province of Heilongjiang will ramp up soybean output by 1.3 million tonnes this...

7. [Study on comparison of the advantages of different soybean producing areas in China from a temporal and spatial perspective](https://iopscience.iop.org/article/10.1088/1742-6596/1592/1/012073) - As one of the important oil crops in China, soybean plays a significant place in the national food s...

8. [[PDF] Report Name: Oilseeds and Products Update - USDA/FAS](https://apps.fas.usda.gov/newgainapi/api/Report/DownloadReportByFileName?fileName=Oilseeds+and+Products+Update_Beijing_China+-+People%27s+Republic+of_CH2025-0184.pdf) - Heilongjiang, China's largest soybean producing province, provided its farmers with 5,250 RMB ($734)...

9. [Soybean Production and Spatial Agglomeration in China from 1949 to 2019](https://www.mdpi.com/2073-445X/11/5/734/pdf?version=1652433463) - ...of soybean production, sown area and yield, spatial-temporal changes in the comparative advantage...

10. [Spatiotemporal Evolution and Influencing Factors of Soybean Production in Heilongjiang Province, China](https://www.mdpi.com/2073-445X/12/12/2090/pdf?version=1700559681) - Heilongjiang Province, as the largest production and supply base for high-quality soybeans in China,...

11. [Soybeans and Oil Crops - Oil Crops Sector at a Glance](http://www.ers.usda.gov/topics/crops/soybeans-and-oil-crops/oil-crops-sector-at-a-glance) - Since 2021, the U.S. soybean crush capacity has expanded and additional crushing capacity is under c...

12. [Soybean processing growth is crushing it - Iowa Soybean Association](https://www.iasoybeans.com/newsroom/article/isr-january-2023-soybean-processing-growth-is-crushing-it) - Iowa has the highest soybean crush capacity of any state (Figure 2) with more than 1.3 million bushe...

13. [U.S. Yield & Production: Production by State | - SoyStats](https://soystats.com/u-s-yield-production-production-by-state/) - Ranking, State, Million Bushels, Million Metric Tons. 1, Illinois, 688, 18.7. 2, Iowa, 597.6, 16.3. ...

14. [Soybean Crush Expansion, 2025 Update](https://soygrowers.com/news-releases/soybean-crush-expansion-2025-update/) - Since 2023, nine new or expanded plants have increased domestic crush capacity while another seven a...

15. [Report Name: Oilseeds and Products Update](https://apps.fas.usda.gov/newgainapi/api/Report/DownloadReportByFileName?fileName=Oilseeds+and+Products+Update_Brasilia_Brazil_BR2025-0017.pdf)

16. [Brazilian Soybean Oil in Global Markets](https://www.brazilianfarmers.com/news/brazilian-soybean-oil-in-global-markets/) - In 2024, Brazil exported 1.37 million tons of soybean oil, yielding USD 1.31 billion in revenue. Ind...

17. [Soybeans in Mato Grosso have a strong productivity review and can ...](https://www.tridge.com/news/soybeans-in-mato-grosso-have-a-strong-produc-dtgvgqfe) - The Association of Soybean Producers of Mato Grosso do Sul (Aprosoja/MS) has revised upwards the pro...

18. [The Use of Long Short-Term Memory Models to Estimate Soybean Pricing: A Regional Climate Data Evaluation From Brazil](https://ieeexplore.ieee.org/document/11025844/) - This work uses machine learning methods to analyze the influence of the Brazilian climate on interna...

19. [GitHub - annapede/Brazil-Soy-Crop-Data: In this repository I present yearly soy cultivation maps. The 30m resolution data used is from MapBiomas.](https://github.com/annapede/Brazil-Soy-Crop-Data) - annapede / **
Brazil-Soy-Crop-Data ** Public

# annapede/Brazil-Soy-Crop-Data

BranchesTags

## Fold...

20. [OF BETA-GLUCOSIDASE AND LEVELS OF ISOFLAVONE 873 ACTIVITY OF BETA-GLUCOSIDASE AND LEVELS OF ISOFLAVONE GLUCOSIDES IN SOYBEAN CULTIVARS AFFECTED BY THE ENVIRONMENT 1](https://www.semanticscholar.org/paper/ceab14688772554ba1f65bb6c6e990087bbd0473)

21. [Gran Rosario area concentrates 80% of the country's oilseed crush capacity](https://web.wbls.com.ar/2021/11/01/gran-rosario-area-concentrates-80-of-the-countrys-oilseed-crush-capacity/index.htm) - Gran Rosario area concentrates 80% of the country's oilseed crush capacity Based on the new survey o...

22. [[PDF] Report Name: Oilseeds and Products Update](https://www.wpsa-aeca.es/aeca_imgs_docs/12258_oilseeds%20and%20products%20update_buenos%20aires_argentina_ar2025-0004.pdf) - In the central agricultural areas which include Buenos Aires and La Pampa provinces, early reports i...

23. [Cómo está la producción de aceites vegetales en Argentina y ...](https://www.agrolatam.com/actualidad/como-esta-la-produccion-de-aceites-vegetales-en-argentina-y-cordoba/) - La producción primaria de granos junto a su industrialización conforma la principal fuente generador...

24. [[PDF] Report Name: Oilseeds and Products Annual - USDA/FAS](https://apps.fas.usda.gov/newgainapi/api/Report/DownloadReportByFileName?fileName=Oilseeds+and+Products+Annual_Buenos+Aires_Argentina_AR2025-0006) - Argentina remains the world's leading exporter of soybean meal and oil, supported by a highly develo...

25. [Crude soya-bean oil exports by country |2024 - WITS - World Bank](https://wits.worldbank.org/trade/comtrade/en/country/ALL/year/2024/tradeflow/Exports/partner/WLD/product/150710) - Crude soya-bean oil imports by country in 2024. Download Excel Sheet ... 2024. 2023. 2022. 2021. 202...

26. [[PDF] Report Name: Oilseeds and Products Update - USDA/FAS](https://apps.fas.usda.gov/newgainapi/api/Report/DownloadReportByFileName?fileName=Oilseeds+and+Products+Update_Buenos+Aires_Argentina_AR2025-0028.pdf)

27. [Argentina veg oil output up in Sep on record crush | Latest Market ...](https://www.argusmedia.com/es/news-and-insights/latest-market-news/2746248-argentina-veg-oil-output-up-in-sep-on-record-crush) - Argentina vegetable oil production set another monthly record in September, as sunflower and soybean...

28. [India's soybean sector needs attention—domestic ...](https://theprint.in/opinion/indias-soybean-sector-needs-attention-domestic-oversupply-but-rising-imports/2571940/) - Despite having a cost advantage, domestic crushers are not purchasing locally grown soybeans, while ...

29. [[PDF] Oilseeds: World Markets and Trade - USDA/FAS](https://apps.fas.usda.gov/psdonline/circulars/oilseeds.pdf) - U.S. soybean oil hit highs last seen in summer 2023, sustained by high petroleum prices and final EP...

30. [World Soybean Oil Trade - Iowa Farm Bureau](https://www.iowafarmbureau.com/Article/World-Soybean-Oil-Trade) - Soybean oil is a vital global commodity. Get insights into production hubs, major importers, and the...

31. [Import volume soybean oil by region 2022/23 | Statista](https://www.statista.com/statistics/620434/soybean-oil-import-volume-worldwide-by-region/) - This statistic shows the import of soybean oil worldwide from in 2022/23, by region.

32. [India's Import of Crude Soybean Oil Decreases By 9%, Valuing at $3.7 Billion in 2024](https://www.indexbox.io/blog/india-crude-soybean-oil-imports-2024/) - Imports of Crude Soybean Oil peaked at 3.9M tons in 2016, however, from 2017 to 2024, imports remain...

33. [Report Name: Oilseeds and Products Update](https://apps.fas.usda.gov/newgainapi/api/Report/DownloadReportByFileName?fileName=Oilseeds+and+Products+Update_New+Delhi_India_IN2024-0041.pdf)

34. [Crude Soybean Oil Imports Soar 116% In First Five Months Of Oil Year: SEA](https://knnindia.co.in/news/newsdetails/sectors/crude-soybean-oil-imports-soar-116-in-first-five-months-of-oil-year-sea) - India's import of crude soybean oil has more than doubled to 19.11 lakh tonne in the first five mont...

35. [[PDF] Oilseeds: World Markets and Trade](https://fas.usda.gov/sites/default/files/2024-05/oilseeds.pdf) - Global oilseed production in 2024/25 is projected at a new record of 687 million tons, up 4 percent ...

36. [[PDF] Report Name: Oilseeds and Products Annual - USDA/FAS](https://apps.fas.usda.gov/newgainapi/api/Report/DownloadReportByFileName?fileName=Oilseeds+and+Products+Annual_Brasilia_Brazil_BR2023-0007) - Post forecasts. 2023/24 soybean production at 159 million metric tons (MMT), up from the estimated 1...

37. [Historical Weather API | Open-Meteo.com](https://open-meteo.com/en/docs/historical-weather-api) - Historical 🌤️ weather data from 1940 onwards with weather records dating back to 1940 and hourly res...

38. [60 years of historical weather as free API and download - Open-Meteo](https://openmeteo.substack.com/p/60-years-of-historical-weather-as) - How we build a fast API based on 20 terabytes of open weather data

39. [nasa-power-api](https://github.com/kdmayer/nasa-power-api) - kdmayer / **
nasa-power-api ** Public

40. [API Data Requests - nasa power](https://power.larc.nasa.gov/docs/tutorials/service-data-request/api/) - POWER Documentation Site

41. [Climate Data Online (CDO)](https://www.ncei.noaa.gov/cdo-web/) - Climate Data Online (CDO) provides free access to NCDC's archive of global historical weather and cl...

42. [ERA5 Hourly - ECMWF Climate Reanalysis - Google for Developers](https://developers.google.com/earth-engine/datasets/catalog/ECMWF_ERA5_HOURLY) - ERA5 is the fifth generation ECMWF atmospheric reanalysis of the global climate. It is produced by t...

43. [Agriculture Historical Weather Data API Documentation](https://www.weatherbit.io/api/ag-weather-api) - Agriculture Historical Weather Data API Documentation.
