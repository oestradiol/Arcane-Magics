# Reading Path (diagram spec)

```mermaid
flowchart LR
  readme[README]
  how[How to read]
  overview[Framework overview]
  claims[Claims and boundaries]
  fi[Framework Interface]
  core[Core theory files]
  apps[Applications Atlas]
  route[Demonstrated route]
  atlas[Research map]
  readme --> how --> overview --> claims --> fi --> core
  claims --> apps
  apps --> route
  apps --> atlas
```

**Paths**

- newcomer: README -> how-to-read -> overview -> claims -> Framework Interface -> core files
- demonstrated-route first: README -> claims -> applications -> demonstrated route -> research docs -> framework
- atlas first: README -> applications -> research map -> selected nodes -> framework
