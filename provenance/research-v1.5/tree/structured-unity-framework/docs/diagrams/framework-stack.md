# Framework Stack (diagram spec)

```mermaid
flowchart TB
  subgraph theory [Theory layers]
    SP[Structural Phenomenology]
    IA[Informational Awareness]
    UD[Unity Dynamics Interface]
  end
  SP --> IA --> UD
  FI -. clarifies .-> SP
  FI -. clarifies .-> IA
  FI -. clarifies .-> UD
  RP[Research Program]
  LG[Literature Guide]
  APP[Applications Atlas]
  DR[Demonstrated Routes]
  RM[Research Map]
  UD --> RP
  theory --> LG
  RP --> APP
  APP --> DR
  APP --> RM
```

**Notes**

- later theory layers extend earlier ones; Interface explains bridges without replacing sources
- Research Program operationalizes Unity Dynamics constraints; Literature Guide routes support for all layers
- Applications split into demonstrated routes and the targeted research map
