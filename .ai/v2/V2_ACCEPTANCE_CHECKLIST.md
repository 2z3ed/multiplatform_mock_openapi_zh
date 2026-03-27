# V2 Acceptance Checklist

## Core positioning
- [ ] V2 clearly upgrades V1 from “客服中台底座” to “客服运营中台”
- [ ] V2 does not leak into V3 scope

## Recommendation center
- [ ] High-intent conversations can generate recommended products
- [ ] Recommendation includes reason and suggested copy
- [ ] Recommendation supports main / substitute / bundle
- [ ] Human confirmation exists before execution behavior
- [ ] Audit logs are recorded

## Follow-up task center
- [ ] System identifies consultation-no-order tasks
- [ ] System identifies unpaid tasks
- [ ] System identifies shipment-exception tasks
- [ ] System identifies after-sale follow-up tasks
- [ ] Tasks have statuses and suggested copy
- [ ] Audit logs are recorded

## Customer tags and profile
- [ ] Customers can receive basic tags
- [ ] Tags include intent / preference / transaction / risk groups
- [ ] Profile snapshot can be viewed in console
- [ ] Manual correction is supported
- [ ] Audit logs are recorded

## Customer operation center
- [ ] Users can filter audiences by tags and states
- [ ] Users can create operation campaigns/tasks
- [ ] Operation flow is preview-first and manually confirmed
- [ ] No large-scale auto-send is implemented
- [ ] Audit logs are recorded

## Analytics
- [ ] Dashboard shows conversation volume
- [ ] Dashboard shows first response time
- [ ] Dashboard shows AI suggestion adoption rate
- [ ] Dashboard shows hot issues
- [ ] Dashboard shows hot products
- [ ] Dashboard shows recommendation usage rate
- [ ] Dashboard shows follow-up task execution rate
- [ ] Dashboard shows conversion trend

## Risk flags
- [ ] Obvious negative sentiment can be flagged
- [ ] Complaint tendency can be flagged
- [ ] Blacklist mark is supported
- [ ] Stop-marketing suggestion is supported
- [ ] Risk flags are visible in console

## Engineering rules
- [ ] All new APIs include OpenAPI annotations
- [ ] All new major features include service-level tests
- [ ] All new major features include API-level tests
- [ ] Provider logic stays separated
- [ ] Unified layer is not broken
- [ ] All important new actions are audited
