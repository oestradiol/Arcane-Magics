# EDU9 — Blocked-Resource Research Rerouting Result — Corrected Report

**Verdict:** `WITHHOLD_EDU9`

```text
records    1640
head       bb871c3f358dab7b185922545bda218eaeef76d3d83ce2a18fc3a1c4c4c8cf2d
sha256     b3d0319ea16b620fcbc11429eb035ac9fd17be1c55e7395b2fa994dbc6c75ca3
evidence   ['NOAA_STATUS', 'NOAA_HOME']
coverage   0.000
precision  0.000
```

The center preserved the unresolved NIST/XLSX obligation, excluded only that blocked packet, rerouted to NOAA, and committed its query before external lookup.

The evidence-selection stage then **failed**. It selected `NOAA_STATUS` and `NOAA_HOME` rather than the resolving `NOAA_NESDIS_END` return. Therefore the stage earned no claim that it had identified the evidential basis for NOAA's event-end judgment.

Disposition:

```text
research routing / problem selection      PASS boundedly
query-before-return                       PASS
blocked prior obligation retained         PASS
explanatory evidence selection            FAIL
EDU9 successor promotion                  WITHHOLD
```

The earlier generated Markdown sentence saying that EDU9 selected the resolving NESDIS return was a reporting defect; the frozen JSON result was already correct and remains controlling.
