# Azure Foundry vs AWS Bedrock — Enterprise agents & generative AI

## Executive summary

- Azure Foundry (Azure AI Foundry / Microsoft Foundry) is a Microsoft enterprise-grade agent & generative-AI platform built for deep integration with Azure, Microsoft 365, Entra ID (Azure AD), and Microsoft governance/IT controls. It is designed to make multi-agent orchestration, publishing to Microsoft 365/Teams, and enterprise governance easy out of the box. See Microsoft docs for the Foundry agent model, connected-agents and publishing flows: [How to use connected agents (Foundry)](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/connected-agents?view=foundry-classic) and [Publish and share agents in Microsoft Foundry](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/publish-agent).
- AWS Bedrock is a multi‑vendor “model supermarket” / managed foundation-model API that emphasizes model choice and serverless scale. Bedrock makes it easy to call Anthropic, Amazon Titan, Meta Llama, Cohere, etc., from AWS infrastructure and to tie models into AWS services (Lambda, S3, CloudWatch). AWS documentation and blog posts describe Bedrock’s model access, pricing modes and governance patterns (e.g., responsible-AI considerations) — see Amazon’s Bedrock coverage in AWS content and Amazon Science overviews (example: Amazon’s model-access article and Bedrock responsible‑AI guidance referenced in AWS materials included in the research results).

### Which to pick (short)

- Choose Azure Foundry if your org is Microsoft/Azure-heavy and you need first‑class Copilot / Teams / M365 integrations, built-in agent publishing, Entra-based identity, agent registry, enterprise governance and policy, and a developer UX for multi-agent workflows.
- Choose AWS Bedrock if you need a cloud-native, model-agnostic marketplace with serverless model invocation and deeper native tie-ins to the broader AWS ecosystem and existing AWS infra/observability patterns.

*(References: Microsoft Foundry docs — connected agents, publishing; platform comparisons and analyses in public cloud AI coverage aggregated in the research.)*

---

## Value proposition: Azure Foundry vs AWS Bedrock (detailed)

### Key Azure Foundry strengths

- Deep Microsoft ecosystem integration: first-class pathways to publish agents into Microsoft 365 Copilot and Teams, Agent 365 registry, and Entra ID identity for agents and RBAC. See: Publish agents to Microsoft 365/Teams and Agent 365 integration notes.
- Agent-first control plane: Foundry exposes "Agent Applications" with stable endpoints, deployments, agent identity, lifecycle (versioning, deployments) and governance controls — reducing the operational work of exposing agents as services.
- Multi‑agent orchestration & tooling: built-in support for connected agents, subagent delegation, no-code and SDK flows for wiring agents together (reduces need to build a custom orchestrator).
- Enterprise governance, compliance & identity: Entra ID identities per published agent, integration with Azure RBAC and Azure Policy, and built-in patterns for reassigning resource permissions post‑publish.
- Developer experience: visual Agent Playground, SDKs, and publishing flows that package an agent into an Agent Application for distribution.

### Key AWS Bedrock strengths

- Model variety and vendor neutrality: direct access to multiple foundation models (Anthropic, Cohere, Meta Llama, Amazon Titan) through a single API; easier to switch models without re‑architecting your stack.
- Serverless invocation patterns & AWS integration: tight coupling to AWS services (Lambda, S3, DynamoDB, CloudWatch), and Bedrock’s scaling & pricing models (on‑demand and provisioned throughput).
- Mature token-based usage modes, and Bedrock-centric tools for evaluation and safety (Bedrock + SageMaker patterns).

### Tradeoffs and practical implications

- Foundry reduces the integration and governance work for enterprise Microsoft customers (publishing, identity, Microsoft 365 distribution). Without Foundry you build identity, endpoints, publishing, RBAC mapping and M365 packaging yourself.
- Bedrock reduces work for teams that need model variety behind a unified API and who already own the AWS infra and data (S3, OpenSearch, Lambda).
- Both platforms evolve quickly; do small pilots to measure latency, cost, and fit for your workloads (RAG, agents, long-context pipelines).

*(Sources: Microsoft Foundry docs; comparative analyses and cloud AI writeups aggregated in research.)*

---

## Anatomy of an agent — canonical components

An effective production agent is more than “an LLM + prompt.” Think in terms of model + harness (the system that turns a raw model into a reliable work engine) and the agent’s runtime architecture.

### Core components (high level)

1. Goal / intent specification — what the agent is meant to accomplish.
2. Model + system prompts — the LLM and its instruction scaffolding.
3. Tools and connectors — callable tools (APIs, DB queries, functions, file search, browser, code execution, etc.).
4. Memory & knowledge — short-term context, persistent memory files or vector stores / retrieval (RAG).
5. Orchestration & planner — decision logic that routes tasks, decomposes goals, and coordinates substeps or subagents.
6. Execution environment & sandbox — safe runtime for tool execution (code runner, containerized hosted agent, or serverless functions).
7. Identity, auth & governance — agent identity, RBAC, approval flows, privacy controls.
8. Telemetry, logging & analytics — observability for prompts, tool calls, errors, hallucination detection and usage/cost monitoring.
9. Policies & guardrails — hard rules for safety, PII handling, allowed actions, human-in‑the‑loop triggers.
10. Human handoff & lifecycle flow — graceful escalation to humans and versioned deployments for production.

### Two useful framing pieces from the literature

- “Agent = Model + Harness” — the harness provides state, tool execution, memory, sandboxing, compaction, and orchestration (LangChain/harness discussion).
- Practical business components (knowledge, configs, business integrations, policies, analytics) — a good checklist for enterprise deployments.

*(See: LangChain blog “The Anatomy of an Agent Harness” and multiple agent-anatomy writeups collected in the research.)*

---

## How to plug many agents from different teams into Azure Foundry — architecture & steps

Foundry’s model: teams build agents inside a Foundry project (dev workspace) → create agent versions → publish as Agent Applications → optionally deploy as hosted/managed deployments or publish to M365/Teams or Agent 365 registry.

### Key primitives you will use

- **Foundry Project:** shared development workspace where teams author agents, indexes and resources.
- **Agent Versions:** immutable snapshots created as you iterate.
- **Agent Application (published):** a managed Azure resource with its own endpoint, Entra agent identity and RBAC scope.
- **Connected Agents / ConnectedAgentToolDefinition:** built-in capability to let a main agent delegate to specialized subagents (no custom orchestrator needed).
- **Agent 365 registry:** organization-wide inventory and management plane for agents (Agent 365 is Microsoft’s admin control plane).

### High-level step-by-step (multi-team pattern)

#### 1. Organizational setup & governance

- Create a Foundry account/project per business unit or a central platform project with dev sandboxes.
- Define roles: Azure AI Project Manager, Azure AI User, Agent publishers, approvers.
- Decide publish scopes: Individual vs Organization.

#### 2. Team development (each team)

- Build agent locally or in Foundry Playground: define instructions, model deployment, tools (OpenAPI tools, Azure Functions, File Search, vector lookups).
- Create agent versions as snapshots for traceability.

#### 3. Use connected agents for composition

- For cross-team reuse, teams should publish specialized agents (e.g., billing_lookup_agent, hr_policy_agent) as published Agent Applications.
- Main orchestrator agents can add these as ConnectedAgentToolDefinition items—Foundry’s main agent routes to them using the provided id/name/description and the main agent need not embed tool code for every domain.
- This reduces replication and centralizes sensitive integrations.

#### 4. Publish and assign identity & permissions

- Each published agent gets a dedicated Agent Application and an Entra agent identity. Reassign RBAC roles the agent needs to access Azure resources (storage, functions, Key Vault).
- For multi‑team reuse, use least‑privilege role assignments on the Agent Application identity.

#### 5. Distribution & lifecycle

- Publish to the Agent Store (internal) or Microsoft 365 / Teams using the built-in publishing flow. For org-wide usage, use Organization scope and Admin approval flows.
- Use Agent 365 to register/discover agents at the tenant level and for centralized monitoring.

#### 6. Observability & operations

- Centralize logs into Azure Monitor / Log Analytics.
- Track per‑agent usage, cost, and safety metrics. Use Azure Policy to enforce allowed configurations.

### Example code sketch (create a connected agent and attach to a main agent — Python pseudocode based on Foundry SDK docs)

```text
code
```

### Operational notes and gotchas

- When published, agents receive distinct identities; you must reassign RBAC grants to the new agent identities for any Azure resources the agent uses.
- Connected agents are limited in depth (Foundry historically enforces depth limits to avoid runaway delegation) — design for a main-orchestrator + specialist subagents model.
- For controllers that must call back to third-party services, prefer using OpenAPI tools or Azure Functions for credentials/secure access rather than embedding secrets in agents.

**Primary references: Microsoft Foundry docs — Connected Agents and Publish flows:**

- Connected agents: [https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/connected-agents?view=foundry-classic](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/connected-agents?view=foundry-classic)
- Publish & Agent Application: [https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/publish-agent](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/publish-agent)
- Publish to M365/Teams: [https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/publish-copilot](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/publish-copilot)
- Agent 365 guide: [https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/agent-365](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/agent-365)

---

## What Azure Foundry saves you from building yourself

Without a platform like Azure Foundry you would have to assemble and operate all of the following pieces yourself:

- Model hosting & routing: model access plus a model router if you need multi-model fallback or per-task routing.
- Agent identity & RBAC lifecycle: creation of unique service identities per agent + automation to grant least-privilege on resource access.
- Stable publishing & versioning endpoints: stable URLs, deployments, rolling updates and traffic routing.
- Multi-agent orchestration primitives: a coordinated delegator, subagent registration and secure call patterns (or build a custom orchestrator).
- M365/Teams packaging and approval flows: manifest authoring, bot provisioning, admin approval integration with Microsoft 365.
- Governance & policy enforcement: audit trails, Azure Policy, policy-as-code for agent deployments.
- Observability & safety tooling: citation tracing, tool call logs, hallucination detection, prompt/response logging with privacy controls.
- Developer UX: Playgrounds, local SDKs, low-code/no-code builders.
- Secrets management for agents and secure connector patterns (Key Vault mapping to agent identities).
- Hosted sandbox/hosted agent infrastructure: container images, autoscaling, region availability and support for hosted agents.

So Foundry reduces both initial engineering time and ongoing operational burden for an enterprise-focused agent program by exposing those features as managed primitives (Agent Applications, publishing experience, Entra identity & RBAC, connected agents, Agent 365 registry).

*(See Microsoft docs pages cited above and platform comparison analysis in the research summary.)*

---

## How to create an agent in Foundry — practical how‑to (and how it differs from an autonomous component)

**Goal:** produce an agent that’s interactive, traceable, secure and composable — and clarify how an “agent” differs from an “autonomous component.”

### Definitions

- **Agent (in Foundry context):** an LLM-driven composition with defined instructions, tools, identity, and an endpoint for invocation (user-driven or via API). Agents are typically interactive, versioned, and published so other consumers can call them.
- **Autonomous component:** a background service or automation that runs continuously or on events (cron/webhook/queue) with little or no interactive user endpoint. It’s typically single-purpose and runs under a service identity but doesn’t expose a conversational or Responses endpoint as an "agent."

### Step-by-step guide to build a Foundry agent (practical)

#### 1. Design & spec

- Define objective, success criteria, SLAs, and allowed tools.
- Decide what data sources the agent needs (indexes, vector stores, SharePoint, SQL).
- Decide human-handoff rules and safety constraints.

#### 2. Build in Foundry project

- Create a new agent in Foundry (Playground or SDK).
- Choose the model deployment (Azure-hosted GPT or other allowed models).
- Add tools: File Search, OpenAPI tool, Azure Function, or Connected agents for domain-specific tasks.
- Add system prompt & few-shot examples to constrain behavior.

#### 3. Local & automated test

- Use the Playground to run representative prompts.
- Unit test tool calls (mock external endpoints).
- Incorporate failure-mode tests (bad data, timeout, missing permission).

#### 4. Version & snapshot

- Create an agent version for traceability before publishing.

#### 5. Publish as Agent Application

- Publish the agent (creates an Agent Application and Deployment).
- Reassign RBAC roles for the published agent identity on resources used by the agent (e.g., storage/Key Vault).
- For Teams/M365 distribution, use the integrated publish-to-M365 flow (prepare metadata, privacy URLs, admin approval if org scope).
- Verify endpoint, protocol (Responses vs Activity protocol), and authentication policy.

#### 6. Operate

- Monitor logs, costs, telemetry; set alerts for error rates and cost spikes.
- Maintain an iteration cadence: update agent versions, publish controlled rollouts.
- Implement usage quotas and guardrails to control runaway behavior.

#### 7. Runbook for incidents & human handoff

- Predefine who gets notified when agent takes risky actions, fails repeatedly or produces PII leaks.
- Implement an “escalate to human” tool/step that transfers conversation context to a human operator with safe data handling.

### Minimal example: agent creation + connected subagent (Python pseudocode — adapt to your SDK/version)

```text
code
```

### How an agent differs from an autonomous component (quick checklist)

- **Invocation:**
  - Agent: user-driven API / chat UI (interactive). Exposes Responses or Activity protocol endpoint.
  - Autonomous component: event-driven (queue/cron) or scheduled workflow; no chat endpoint.
- **Identity & visibility:**
  - Agent: has published Agent Application and unique agent identity (audit trail) — created for traceability.
  - Autonomous component: typical service principal/service identity; may be less tightly integrated into the Agent registry.
- **Orchestration:**
  - Agent: routes to tools, can delegate to sub-agents, and can be called by other agents.
  - Autonomous component: runs a process; may call LLMs internally but not present itself as an interactive conversational resource.
- **Human in the loop:**
  - Agents often include handoff UX and explicit user-facing behavior.
  - Autonomous components usually have operational alerts and logs but no end-user chat handoff.

### Best practices and guardrails

- Identity: use least privilege and reassign RBAC after publish.
- Observability: log prompts, tool calls, and citations — but redact PII before storing logs.
- Cost control: rate-limits, provisioning limits, and scheduled shutdown for hosted agents.
- Safety: mandatory policy layer/filters, human escalation triggers, and testing harness for risky actions.
- Versioning & rollback: publish agent versions and have a plan to rollback the Agent Application deployment.
- Reuse: publish specialized agents (billing, HR lookup) and compose with connected agents to avoid duplication.

*(References: Foundry publish docs and connected agents docs linked earlier.)*

---

## Example decision scenarios — when Foundry is the right strategic move

- You need enterprise-safe, governed agent catalog integrated with Microsoft 365 and Teams (Foundry + Agent 365 + M365 publishing flows).
- You want corporate identity-based access control where agents share Entra-based permissioning and auditing.
- You want a multi-team agent program with discoverability, an internal store, and lifecycle management (versioning, deployments, RBAC).

If your priorities are model-agnostic experimentation across many third-party models or you’re heavily AWS-native and prioritize serverless model calls integrated into S3/Lambda pipelines, Bedrock is a strong candidate.

*(See Microsoft Foundry docs and platform comparison analyses in the research.)*

---

## Short checklist to start a pilot (recommended)

1. Pick a single enterprise workflow (e.g., contract-review assistant) that needs document access + compliance.
2. Build an agent in Foundry: model + File Search + compliance checks as a connected compliance subagent.
3. Test in Foundry Playground and write safety tests.
4. Publish as Agent Application internal-scope; assign RBAC to agent identity for the resources it needs.
5. Deploy to a small group and observe logs, costs and safety signals.
6. Iterate, document runbooks and prepare org-wide publishing (Agent 365 registration + M365 Teams packaging if needed).

---

## Useful links from the research (jump-to references)

- Foundry connected agents (multi-agent orchestration): [https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/connected-agents?view=foundry-classic](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/connected-agents?view=foundry-classic)
- Publish & Agent Application concepts: [https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/publish-agent](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/publish-agent)
- Publish to Microsoft 365 / Teams: [https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/publish-copilot](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/publish-copilot)
- Agent 365 (digital worker & tenant registry): [https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/agent-365](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/agent-365)
- LangChain — harness & agent architecture: LangChain blog “The Anatomy of an Agent Harness” (coverage in collected research)
- AWS Bedrock / Amazon Bedrock model access & responsible AI guidance: AWS/Amazon content and Amazon Science model access writeups referenced in the platform comparison research
