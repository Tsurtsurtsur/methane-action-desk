# CH₄ Action Desk — Türkiye pilot

A public-interest, open-source prototype for following up methane plume observations at ten waste sites in Türkiye. **Zero methane reductions are independently verified by this project to date.** This does not imply that operators have not taken action.

Website: https://methane-action-desk.vercel.app

## Sources and scientific cautions

- [UCLA STOP Methane (2026)](https://law.ucla.edu/news/spotlight-top-methane-sources-turkeys-waste-sector) — Tanager-1 observations, Jan 2025–Jun 2026, at least two detected plumes per site.
- [Guardian reporting](https://www.theguardian.com/environment/2026/oct/05/methane-mega-leaks-from-un-climate-summit-host-turkey) and [site-level rate graphic](https://interactive.guim.co.uk/uploader/embed/2026/09/turkey_methane/giv-32554nJIXUjNjxjVf/).
- The listed rates are **averages among detections**, not verified continuous emissions. Do not multiply them by 8,760 to claim annual emissions or avoided emissions. Sum of detection averages is descriptive, not a contemporaneous measured total.
- Site names are geographic descriptors, not validated facility boundaries. Potential operators may be unknown or cited in media reporting only. No accusations or claims of responsibility should be drawn from an unverified attribution.
- The Guardian graphic and UCLA article describe different end dates; resolve this discrepancy before making formal temporal comparisons.
- Do not redistribute imagery or full proprietary plume datasets unless permissions allow it. This tracker uses published summary values with attribution.
- UCLA, Carbon Mapper and Guardian have **not** endorsed or partnered with this project.

## Local run and verification

Run \`python -m http.server 8000 --directory public\`, then open http://localhost:8000.

Run \`python scripts/verify_data.py\` and \`python -m unittest discover -s tests\`.

Host as a static site with \`public\` set as the output directory. No accounts, credentials, third-party scripts, API keys or background tracking are required.

## What constitutes verified impact?

1. Map satellite detection geometry to the actual operator and identify the correct parties.
2. Obtain dated operator/regulator response and specific remediation work records.
3. Acquire comparable independent before-and-after measurements including limitations and counterfactual.
4. Only record tonnes avoided with defensible independent evidence and public source references.

To submit corrections, open a GitHub issue with a dated public source URL. Do not post non-public personal information. The project is a proof of concept; GitHub issues do not represent official complaints or regulatory actions.

Original code is MIT licensed. Source data and media retain their owners' licenses.

## Deployment

The static dashboard is published at https://methane-action-desk.vercel.app. The production branch is `main`; this repository is linked in Vercel for automatic deployment. This documentation update also serves as a non-functional deployment integration check.
