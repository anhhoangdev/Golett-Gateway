| Priority | Fix                                                                    | Effort  | Pay-off                                      |
| -------- | ---------------------------------------------------------------------- | ------- | -------------------------------------------- |
| **P0**   | Replace in-proc EventBus with Redis Streams; add DLQ for failed events | Medium  | Prevents data loss in prod                   |
| **P0**   | Implement `SummariserWorker`; time-boxed per chunk                     | Medium  | Controls short-term context size             |
| **P1**   | YAML-driven promotion policies per `memory_type`                       | Low     | Business can tune without redeploy           |
| **P1**   | Introduce Planner + Critic agents; wire to orchestrator parallel mode  | Medium  | Autonomy & result accuracy                   |
| **P2**   | `ingest_doc` & `ingest_sql` tools for live KB updates                  | Medium  | Key BI use-case (ad-hoc CSV / SQL)           |
| **P2**   | Guard-rail middleware: loop cap, numeric-source check                  | Low–Med | Safety & trust                               |
| **P3**   | GraphStore layer for KPI lineage & entity links                        | High    | Advanced reasoning, duplicate-fact avoidance |
