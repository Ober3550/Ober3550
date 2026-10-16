# Oliver

**Location:** Brisbane  
**Email:** Ober3550@gmail.com  
**Phone:** 0407 336 755  
**LinkedIn:** https://www.linkedin.com/in/oliver-mainey/  

## Summary

I'm a Software Engineer with 5+ years building production systems in ad-tech, fintech, e-commerce and aged care. I focus on performance, testing and developer tooling. Outside work I'm passionate about high-performance computing and simulation science. I've built fluid and gravity simulations, and I keep up with new language features and optimisation techniques. Most recently I built a tool that searches all 4.3 billion Factorio seeds for the ideal Space Exploration playthrough and can generate the surface of any planet or moon on demand, using multi-core CPU and GPU compute.

## Core Skills

| Category               | Technologies                                                                                                                                                         |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Languages              | C++ (SIMD), C, Rust, Zig, Golang, C#, Java, Python, TypeScript/JavaScript, MATLAB, SQL, Bash, Kotlin, Swift, F#, Lua, Groovy, PHP, R, XSLT, HTML/CSS                 |
| Backend / Services     | .NET, Node.js, Bun, JMS, ActiveMQ, Laravel                                                                                                                           |
| Frameworks & UI        | React Native, Next.js, Vue, HTMX, Angular, DearImGui, SDL2, SFML, OpenGL, P5.js, Google Web Toolkit                                                                  |
| Cloud & Infra          | AWS, GCP, Azure DevOps, GitHub Actions, Docker, Kubernetes, Helm, Terraform, Nginx, Jenkins, Linux                                                                   |
| Testing & Quality      | Jest, JUnit, Cucumber, Selenium, Chromedriver, WebdriverIO, Appium, Mountebank, Imposter.sh                                                                          |
| Data & Monitoring      | PostgreSQL, MySQL, SQLite, Oracle, BigQuery, RESTful, gRPC, Protobuf, Azure App Insights, Google Analytics, Grafana                                                  |
| Tooling & Productivity | Claude Code, GPT-5.6 Sol, Deepseek V4 pro, Deepseek Harness, Pi Agent, OpenClaw, GitHub, Bitbucket, Jira, Confluence, Docmosis, LibreOffice, Agentic AI, Custom MCPs |
| Strength Themes        | Data oriented design, performance profiling, multi-scale testing, developer productivity oriented and robust design                                                  |

## Experience

### Trilogy Care – Software Engineer

_October 2025 – August 2026_  
_Home care provider: nursing, cleaning, gardening, meals and home modifications_

- Built features for the new client mobile and web app (React Native, PHP/Laravel): incident reporting, service leave requests, contact management, profile updates and document sign-off.
- Built and maintained internal systems (PHP/Laravel, Vue) supporting operations, care coordination and billing.
- Developed a claims classification app (Next.js) that maps invoice line items to government funding categories, so each claim is billed against the right budget.

### Domino’s – Software Engineer

_April 2023 – September 2025_  
_Global delivery and pickup search across 9 markets: Australia/NZ, Japan, Singapore, Malaysia, Taiwan, Germany, France and the Netherlands_

- Extended Google Maps store search and address lookup to Germany, France, Taiwan, Japan and Malaysia (React Native, Jest, Chromedriver), handling local address formats and modernising the UI.
- Extended various backend search microservices for internal business operations (C#/.NET, Swagger).
- Designed and built a package management workflow for Imposter.sh mock definitions, letting teams share and version API mocks.
- Containerised .NET and Node services, standardised Azure DevOps pipelines, and refined Kubernetes deployment patterns and error reporting with Helm.

### CitrusAd – Software Engineer

_March 2022 – April 2023_  
_Retail media platform: 500M ad requests a day for Coles, Woolworths, Target and 100+ retailers, serving 3.5k brands_

- Worked on ad relevancy services (Go, PostgreSQL, BigQuery), focusing on latency and ranking correctness.
- Delivered the Seller ID feature (Go, Java, BigQuery), letting multiple sellers advertise the same product with correct impression and click-through reporting.
- Owned the rollout to all retailers on the live system, managing the re-index of 20 billion ad events over two weeks of 9am–12am shifts.
- Built a debugging tool (Node, Docker, Kubernetes, Terraform) that tracked deployed service versions and redirected platform traffic to local instances.

### GBST – Graduate Software Engineer

_Jan 2021 – March 2022_  
_Wealth management software for NAB, Westpac, UniSuper and others_

- Wrote a TLE-to-Groovy transpiler (5k lines, Node) and a Groovy test client (5k lines, Java, Spring, JUnit), modernising 2 million lines of legacy scripts.
- Enhanced the Retail Cash Accounts module (Java, GWT, PostgreSQL), extending transactions beyond private banking and pensions.
- Supported the CHESS-to-CSP integration with message-driven architecture (ActiveMQ, JMS).

## Projects

### [SolarSim: N-body gravity simulation](https://github.com/ober3550/SolarSim) (C++, SIMD, multithreading, OpenGL, DearImGui)

- Real-time gravitational simulation of 20,000+ bodies, computing every pairwise interaction (O(n²)) and kept fast with SIMD and multithreading.
- 2D and 3D versions with orbital path tracing, collisions that merge bodies, and shaded rendering.

### [seed-search: procedural universe and planet generator](https://github.com/ober3550/seed-search) (Zig, WebGPU, WebAssembly)

- Rebuilt a game's Lua generator for star systems, planets and terrain in Zig, matching the original output exactly. It's checked against the Lua by an automated comparison harness.
- Scanned all ~2.15 billion distinct universes using multi-core CPU and WebGPU compute kernels. Any planet surface can be generated in the browser via WebAssembly: [live surface demo](https://ober3550.github.io/seed-search/surface.html?mod=se&target=Nauvis&seed=2606936850).

### [factorio-ai: MCP server for AI agents](https://github.com/ober3550/factorio-ai) (TypeScript, Lua, MCP)

- Lets AI agents such as Claude play Factorio. A TypeScript bridge talks to an in-game Lua mod over RCON, exposing 56 tools for observing the world, building, and planning blueprints.

## Education

**Queensland University of Technology**  
Bachelor of Information Technology (Distinction)  
Majors: Computer Science and Simulation Science  
Focus: physical simulation with high-performance C++ and data visualisation (MATLAB, Matplotlib, OpenGL)
