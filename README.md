# Container redemption business plan

[![CI](https://github.com/wbp318/maine-business-2027/actions/workflows/ci.yml/badge.svg)](https://github.com/wbp318/maine-business-2027/actions/workflows/ci.yml) [![Open questions](https://img.shields.io/github/issues/wbp318/maine-business-2027/question?label=open%20questions&color=d876e3)](https://github.com/wbp318/maine-business-2027/issues?q=is%3Aopen+label%3Aquestion)

Planning repo for a beverage container redemption business. It started as a plan for Maine and moved to Georgia in November 2026.

## Where things stand

| Folder | State | Status |
| --- | --- | --- |
| [georgia](https://github.com/wbp318/maine-business-2027/tree/main/georgia) | Georgia | Active. Georgia has no deposit law yet, so this is a brief on the politics, the possible program designs, and what to do while a law is written |
| [maine](https://github.com/wbp318/maine-business-2027/tree/main/maine) | Maine | Archived. A full plan for a licensed redemption center under Maine's existing law, with grants, internships, and side-business research. The Maine partner left, so it has no site or operator |

Start with the [Georgia brief](https://github.com/wbp318/maine-business-2027/blob/main/georgia/README.md).

## Why Georgia, and the catch

Georgia elected a new governor on November 3, 2026, and a bottle recycling program was among the things she said she intends to pass. A new deposit law in a state of about 11 million people would open a large market at once.

The catch is that the business only exists if the law pays independent redemption centers a handling fee, as Maine's does. Some deposit laws have beverage producers run redemption themselves. Until a bill is filed we don't know which kind Georgia would get, and deposits would start well after a bill passes.

## Repo layout

| Path | What it is |
| --- | --- |
| [georgia/](https://github.com/wbp318/maine-business-2027/tree/main/georgia) | The Georgia brief |
| [maine/](https://github.com/wbp318/maine-business-2027/tree/main/maine) | The archived Maine plan: [PLAN.md](https://github.com/wbp318/maine-business-2027/blob/main/maine/PLAN.md), diagrams, grants, ideas, internships, correspondence |
| [scripts/build_docs.py](https://github.com/wbp318/maine-business-2027/blob/main/scripts/build_docs.py) | Rebuilds the Maine plan's PLAN.md and README charts |
| [.github/workflows/ci.yml](https://github.com/wbp318/maine-business-2027/blob/main/.github/workflows/ci.yml) | CI: keeps the Maine docs in sync, renders every Mermaid diagram, checks the plan HTML, blocks private files, reports dead links |
| [LICENSE](https://github.com/wbp318/maine-business-2027/blob/main/LICENSE) | All rights reserved. Viewing only |

## License

Copyright (c) 2026 William Brooks Parker. All rights reserved. This repository is published for viewing only; see [LICENSE](https://github.com/wbp318/maine-business-2027/blob/main/LICENSE).
