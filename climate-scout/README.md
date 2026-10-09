# Climate Action Scout: 30-day evidence-to-action trial (9 Oct–9 Nov 2026)

This experimental program examines **implementation bottlenecks in climate mitigation** without assuming methane satellite monitoring is the optimal leverage point. The methane monitor continues independently.

Public site: https://methane-action-desk.vercel.app/opportunities.html
Primary machine-readable data: `public/data/opportunities.json`.

## Research tracks
1. Local-government solar delivery and utilization of existing grants.
2. Grid connection, storage, electrification barriers.
3. Industrial energy-efficiency retrofits.
4. Methane repairs and short-lived climate pollutants.
5. International implementation barriers / financing gaps with identifiable action.

## Verification protocol
For every lead record a dated **primary source**, what is known, what is missing, responsible actor if confirmed, whether a deadline is open, and a 30-day next step. A fiscal appropriation or grant award is not evidence that a specific project is delayed. Never infer an available budget from historical utilization data. Prefer fixing a **real named project** over creating another monitoring dashboard. Compare expected impact, tractability, probability of influencing the outcome, time-cost and counterfactual explicitly; never invent avoided tCO2e.

Stages:
- researching_bottleneck: documented systemic gap, no responsible project yet;
- watching_delivery: funded program, delivery status unverified;
- initial_screening: open channel that may be relevant; technical evidence not yet assessed;
- monitoring_no_partner: source monitored, no remediation partner;
- actionable: named actor, verified bottleneck and feasible intervention;
- intervention_in_progress: partner confirms work;
- independently_verified: independent abatement measurement with defensible counterfactual.

Set `independent_verified_abatement_tco2e` > 0 only after credible publicly cited independent verification. Otherwise preserve 0. No automatic mass outreach, unconsented emails, attribution of misconduct, funding commitment, or authorization to represent an external institution.

## Operations
A weekly ChatGPT automation is instructed to research new primary sources, deduplicate leads and update this JSON through the connected GitHub app. GitHub is linked to Vercel; commits on `main` redeploy the public page. **This GitHub repo alone does not run an autonomous research agent.** The automation depends on access to the relevant connected tools and can fail. Review health and logs in GitHub and ChatGPT tasks. Methane ingestion remains separately scheduled.

As-of 9 Oct 2026 official source highlights:
- Israel State Comptroller, June 2026: ~NIS 39m utilized out of NIS 248m allocated in local government energy calls for 2021–25, **as of June 2025**; this does not prove present availability. https://library.mevaker.gov.il/sites/DigitalLibrary/Pages/Publications/2153.aspx
- Israel Ministry of Energy, Jul 2026: 42 grantees selected for solar sports canopy program; construction status unknown. https://www.gov.il/he/pages/news-220726-2
- Israeli Energy Ministry public consultation on offshore oil/gas decommissioning, published Oct 7; remote meeting Dec 2 with registration Nov 26. Climate benefit of possible submissions *not yet established*. https://www.gov.il/he/pages/decommissioning-071026
