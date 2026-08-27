# CORTEX LEDGER AI

## Every Decision Traced. Every Agent Accountable.

**Company:** Orvyn Workx AI  
**Platform:** Cortex Ledger AI  
**Primary Business Application:** Business Operations  
**Project Priority:** Project 1 — Cortex Ledger AI  
**Primary Engineering Objective:** Build a production-oriented agentic AI operating system capable of orchestrating frontier models, external agent runtimes, specialized business agents, tools, MCP servers, knowledge graphs, memory, approvals, autonomous workflows, evaluation, and secure execution.

---

# 1. EXECUTIVE DIRECTIVE

You are Claude Code acting as:

> Lead AI Systems Engineer + Agentic AI Architect

Your job is to build **Cortex Ledger AI**, not a collection of disconnected AI demos.

Cortex Ledger AI is the intelligence, knowledge, orchestration, and execution layer behind the Business Operations ecosystem.

Core positioning:

> **Cortex Ledger AI — Every decision traced. Every agent accountable.**

Cortex Ledger AI should eventually allow organizations to deploy AI systems that can:

- understand objectives
- understand the systems they operate on
- inspect business and technical knowledge
- plan tasks
- discover specialized agents
- select appropriate models
- delegate work
- use tools
- access MCP services
- access approved business data
- collaborate with other agents
- request human approval
- execute actions
- verify results
- remember relevant information
- evaluate performance
- maintain complete execution traces
- operate within security boundaries

---

# 2. PROJECT STRATEGY

The original project concept contained approximately 15 separate AI solutions.

Do NOT build those as separate projects right now.

The first priority is building the infrastructure that can eventually power them.

Roadmap:

PROJECT 1
CORTEX LEDGER AI
Agentic AI Operating System

        ↓

PROJECT 2
BUSINESS OPERATIONS
Autonomous Business / Workforce Operations

        ↓

PROJECT 3
CORTEX LEDGER AI SWE
AI Software Engineering Agent

        ↓

PROJECT 4
CORTEX LEDGER AI SENTINEL
AI Incident Response Agent

        ↓

PROJECT 5
CORTEX LEDGER AI EVAL
AI Agent Evaluation Platform

        ↓

PROJECT 6
CORTEX LEDGER AI GUARD
AI Agent Security Platform

Do not begin Projects 2–6 until Project 1 has a functional foundation.

---

# 3. THE CORTEX LEDGER AI THREE-PILLAR ARCHITECTURE

Cortex Ledger AI is built around three primary infrastructure layers:

1. AGENT FABRIC
2. KNOWLEDGE FABRIC
3. EXECUTION ENGINE

These answer three fundamental questions:

AGENT FABRIC
> WHO should perform the work?

KNOWLEDGE FABRIC
> WHAT does the system need to understand?

EXECUTION ENGINE
> HOW should the work be performed safely?

Architecture:

                         CORTEX LEDGER AI
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
          ▼                 ▼                 ▼
    AGENT FABRIC       KNOWLEDGE FABRIC   EXECUTION ENGINE
          │                 │                 │
     237 Agents           GRAPHIFY          Claude
     Capabilities         Codebase          Hermes
     Permissions          Architecture      Native Agents
     Tools                Dependencies      Tools
     Teams                Documentation     MCP
          │                 │                 │
          └─────────────────┼─────────────────┘
                            │
                    BUSINESS OPERATIONS

These layers must remain modular.

---

# 4. CORTEX LEDGER AI CONTROL PLANE

Cortex Ledger AI is the control plane.

External systems are not the control plane.

This includes:

- Claude
- Hermes
- individual agents
- MCP servers
- external tools
- model providers

Cortex Ledger AI controls:

- identity
- discovery
- authorization
- routing
- budgets
- policies
- approvals
- execution
- memory access
- knowledge access
- observability
- evaluation

Conceptually:

                         CORTEX LEDGER AI
                      CONTROL PLANE
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   AGENT FABRIC       KNOWLEDGE FABRIC    EXECUTION ENGINE
        │                   │                   │
     Agents              Graphify          Backends
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                         POLICY
                            │
                       PERMISSIONS
                            │
                         AUDIT

---

# 5. AGENT FABRIC

The Agent Fabric answers:

> "WHO should perform this task?"

The Agent Fabric contains:

- Agent Registry
- Agent Profiles
- Agent Discovery
- Agent Router
- Agent Invocation Gateway
- Agent Teams
- Agent Permissions
- Agent Budgets
- Agent Memory
- Agent Performance
- Agent Evaluation
- Agent Lifecycle Management

The existing library of approximately 237 specialized agency agents becomes part of the Cortex Ledger AI Agent Fabric.

The 237 agents are infrastructure.

They are NOT 237 disconnected applications.

---

# 6. THE 237-AGENT LIBRARY

Cortex Ledger AI must support the existing agency agent library.

Do not assume the library contains exactly 237 agents until it has been programmatically inspected.

The system must:

1. locate the existing agent library
2. count agents
3. inspect their source format
4. identify categories
5. identify capabilities
6. identify dependencies
7. identify tools
8. identify memory requirements
9. identify external API requirements
10. normalize them into Cortex Ledger AI-compatible representations

If the agents are stored as:

- Markdown
- JSON
- YAML
- Python
- TypeScript
- prompts
- configuration files
- database records
- another format

inspect the actual source before designing the importer.

Do NOT manually recreate 237 agents if an existing source of truth exists.

---

# 7. CORTEX LEDGER AI AGENT FABRIC

Conceptual architecture:

                     CORTEX LEDGER AI AGENT FABRIC
                              │
             ┌────────────────┼────────────────┐
             │                │                │
        REGISTRY          DISCOVERY          ROUTER
             │                │                │
             └────────────────┼────────────────┘
                              │
                     INVOCATION GATEWAY
                              │
              ┌───────────────┼───────────────┐
              │               │               │
          Permissions       Budgets          Policy
              │               │               │
              └───────────────┼───────────────┘
                              │
                        AGENT EXECUTION
                              │
                     ┌────────┼────────┐
                     │        │        │
                  Native   Hermes    Future
                  Agents             Runtimes

---

# 8. AGENT REGISTRY

The Agent Registry is the source of truth for Cortex Ledger AI agents.

Each agent should eventually have a structured profile.

Example:

agent_id:
    marketing_017

name:
    Campaign Strategist

category:
    Marketing

description:
    Develops marketing campaigns,
    positioning, audience strategies,
    and campaign plans.

capabilities:
    - campaign_strategy
    - audience_research
    - positioning
    - content_strategy

backend:
    type: axiom_native

tools:
    - web_search
    - analytics

permissions:
    - data.read
    - marketing.write

risk_level:
    medium

budget:
    max_tokens: 50000
    max_execution_seconds: 300

The schema should be refined based on actual implementation requirements.

Do not create unnecessary metadata solely for appearance.

---

# 9. AGENT DISCOVERY

Cortex Ledger AI must NOT load all 237 agents into every model context.

Use:

# LAZY AGENT DISCOVERY

Workflow:

User Task
   ↓
Task Classification
   ↓
Capability Search
   ↓
Agent Registry
   ↓
Top Candidate Agents
   ↓
Permission Check
   ↓
Agent Selection
   ↓
Load Selected Agent
   ↓
Execute

Benefits:

- lower context usage
- lower cost
- lower latency
- better security
- better scalability

---

# 10. AGENT ROUTER

Build an:

# CORTEX LEDGER AI AGENT ROUTER

The router determines which agent or team should handle a task.

Eventually consider:

- capability
- specialization
- historical performance
- availability
- cost
- latency
- risk
- required tools
- required knowledge
- required memory
- backend
- task complexity
- current workload

Version 1:

Explicit routing.

Version 2:

Capability routing.

Version 3:

Multi-factor routing.

Version 4:

Evaluation-informed routing.

Do not jump directly to Version 4.

---

# 11. AGENT INVOCATION GATEWAY

All external requests to the agent library must pass through:

# AGENT INVOCATION GATEWAY

Conceptual operations:

discover_agents()
get_agent()
check_agent_permission()
invoke_agent()
get_agent_status()
get_agent_capabilities()

The actual API should be implemented according to the repository architecture.

The gateway must enforce:

- authentication
- authorization
- tenant isolation
- permissions
- budgets
- rate limits
- risk controls
- audit logging
- execution tracking

---

# 12. HERMES ACCESS TO AGENT FABRIC

Hermes must NEVER receive unrestricted access to the 237 agents.

Hermes must interact with the Agent Fabric through Cortex Ledger AI-controlled interfaces.

Architecture:

                         HERMES
                            │
                     Agent Request
                            ↓
                  CORTEX LEDGER AI AGENT GATEWAY
                            │
                     Authorization
                            │
                       Budget Check
                            │
                       Risk Check
                            │
                     Agent Discovery
                            │
                      Agent Router
                            │
                    Agent Invocation
                            │
                        Execution
                            │
                         Audit
                            │
                          Result
                            ↓
                         HERMES

Hermes must never:

- directly manipulate the registry
- bypass permissions
- bypass budgets
- bypass policy
- bypass approval requirements
- access all agents automatically
- access all tools automatically
- access all memory automatically
- access production systems without authorization

---

# 13. AGENT BUDGETS

Every agent invocation should eventually support:

- token budget
- time budget
- tool call budget
- delegation budget
- API cost budget
- memory retrieval budget
- concurrency budget

Example:

budget:
    max_tokens: 25000
    max_seconds: 180
    max_tool_calls: 15
    max_delegations: 3

---

# 14. AGENT RECURSION PROTECTION

Prevent:

Agent A
 ↓
Agent B
 ↓
Agent C
 ↓
Agent A
 ↓
Agent B
 ↓
...

Implement:

- maximum delegation depth
- execution timeout
- token budget
- invocation budget
- cycle detection

---

# 15. AGENT TEAMS

Cortex Ledger AI should support temporary agent teams.

Example:

                 STRATEGY DIRECTOR
                         │
          ┌──────────────┼──────────────┐
          │              │              │
       Research       Finance       Marketing
        Agent          Agent          Agent
          │              │              │
          └──────────────┼──────────────┘
                         ↓
                     Synthesis

Teams should be dynamically created for tasks.

---

# 16. KNOWLEDGE FABRIC

The Knowledge Fabric answers:

> "WHAT does Cortex Ledger AI need to understand before acting?"

The Knowledge Fabric is built around:

# GRAPHIFY

Graphify becomes a first-class Cortex Ledger AI knowledge subsystem.

The current Graphify project describes itself as turning codebases and related artifacts into a queryable knowledge graph, with local AST-based code extraction, explainable graph relationships, querying, path tracing, and MCP support. :contentReference[oaicite:1]{index=1}

Repository:

:contentReference[oaicite:2]{index=2}

Do not treat Graphify as a decorative visualization.

Treat it as a Knowledge Fabric capability.

---

# 17. GRAPHIFY ROLE

Graphify provides structured understanding of:

- source code
- modules
- functions
- classes
- dependencies
- APIs
- documentation
- configuration
- schemas
- project relationships
- architecture

Conceptually:

                    GRAPHIFY
                       │
       ┌───────────────┼────────────────┐
       │               │                │
      CODE        ARCHITECTURE      DOCUMENTATION
       │               │                │
       ├─ Files        ├─ Modules       ├─ README
       ├─ Functions    ├─ Services      ├─ Docs
       ├─ Classes      ├─ APIs          ├─ Specs
       └─ Symbols      └─ Dependencies  └─ Knowledge

---

# 18. GRAPHIFY MUST BE INSPECTED FIRST

Before integrating Graphify:

1. inspect repository
2. inspect README
3. inspect package configuration
4. inspect source structure
5. identify language
6. identify framework
7. identify installation
8. identify CLI
9. identify APIs
10. identify SDK
11. identify graph representation
12. identify indexing pipeline
13. identify parsing
14. identify dependency analysis
15. identify query capabilities
16. identify MCP support
17. identify visualization
18. inspect tests
19. inspect licensing
20. determine local deployment options
21. determine service deployment options

Do NOT invent Graphify APIs.

The actual repository implementation is the source of truth.

Create:

docs/graphify/GRAPHIFY_AUDIT.md

Then:

docs/graphify/GRAPHIFY_INTEGRATION.md

---

# 19. KNOWLEDGE GATEWAY

Create a standardized Cortex Ledger AI Knowledge Gateway.

Conceptual interface:

knowledge_gateway.search()

knowledge_gateway.query()

knowledge_gateway.get_node()

knowledge_gateway.get_neighbors()

knowledge_gateway.get_dependencies()

knowledge_gateway.get_dependents()

knowledge_gateway.get_architecture()

knowledge_gateway.get_documentation()

knowledge_gateway.get_impact()

knowledge_gateway.get_path()

The exact interface must be based on Graphify's real capabilities.

Do not expose unsupported operations.

---

# 20. GRAPHIFY ADAPTER

Create:

packages/axiom-graphify/

Potential structure:

packages/axiom-graphify/
├── adapter/
├── client/
├── knowledge/
├── indexing/
├── queries/
├── permissions/
├── models/
└── tests/

The final structure may change after Graphify inspection.

---

# 21. GRAPHIFY + AGENT FABRIC

Graphify and the Agent Fabric must work together.

Example:

USER:

"Fix the authentication issue."

        ↓

CORTEX LEDGER AI

        ↓

GRAPHIFY

        ↓

Understand repository

        ↓

Find authentication subsystem

        ↓

Find relevant modules

        ↓

Find dependencies

        ↓

Determine blast radius

        ↓

AGENT FABRIC

        ↓

Discover software engineering agents

        ↓

Select appropriate agent

        ↓

EXECUTION ENGINE

        ↓

Claude / Hermes / Native Agent

        ↓

Authorized tools

        ↓

Tests

        ↓

GRAPHIFY RE-ANALYSIS

        ↓

Evaluation

        ↓

Human Approval if required

        ↓

Result

---

# 22. GRAPHIFY + HERMES

Hermes must not receive unrestricted access to Graphify.

Hermes interacts through Cortex Ledger AI.

Architecture:

                    HERMES
                       │
                       ↓
                CORTEX LEDGER AI GATEWAY
                       │
                 Permission
                       │
                Knowledge Request
                       │
                       ↓
                    GRAPHIFY
                       │
                       ↓
                 Knowledge Result
                       │
                       ↓
                CORTEX LEDGER AI VALIDATION
                       │
                       ↓
                    HERMES

Hermes cannot directly manipulate:

- Graphify database
- graph files
- indexes
- repositories
- knowledge stores

unless explicitly authorized through Cortex Ledger AI.

---

# 23. KNOWLEDGE PERMISSIONS

Potential scopes:

repository.read
code.read
architecture.read
dependency.read
documentation.read
knowledge.search
knowledge.query
knowledge.export

Modification capabilities belong to the Execution Engine and require separate authorization.

---

# 24. GRAPHIFY VS CORTEX LEDGER AI MEMORY

Do not confuse these systems.

GRAPHIFY:

Structured knowledge about systems.

Examples:

- code
- architecture
- dependencies
- documentation
- repository relationships

CORTEX LEDGER AI MEMORY:

Information retained from execution.

Examples:

- task state
- agent observations
- business context
- workflow history
- user-approved facts

They may communicate through controlled interfaces.

They are not the same subsystem.

---

# 25. EXECUTION ENGINE

The Execution Engine answers:

> "HOW is the work performed?"

The Execution Engine orchestrates:

- frontier models
- native agents
- Hermes
- tools
- MCP
- subprocesses
- external services
- business systems

Architecture:

                       EXECUTION ENGINE
                              │
            ┌─────────────────┼─────────────────┐
            │                 │                 │
          MODELS           AGENTS             TOOLS
            │                 │                 │
         Claude            Hermes            MCP
         OpenAI            Native            APIs
         Google            Future            Services

---

# 26. MODEL GATEWAY

Keep the Model Gateway separate from the Agent Gateway.

MODEL GATEWAY:

- Anthropic
- OpenAI
- Google
- future providers
- local models

AGENT GATEWAY:

- Cortex Ledger AI Native Agents
- Hermes
- future external agent runtimes

Architecture:

                    CORTEX LEDGER AI
                       │
             ┌─────────┴─────────┐
             │                   │
       MODEL GATEWAY        AGENT GATEWAY
             │                   │
      ┌──────┼──────┐      ┌─────┼─────┐
      │      │      │      │     │     │
   Claude  OpenAI  Gemini Cortex Ledger AI Hermes Future

---

# 27. ANTHROPIC

Anthropic is the primary frontier model integration for Project 1.

Implement through a provider-neutral abstraction.

Do not hard-code Anthropic logic throughout Cortex Ledger AI Core.

---

# 28. HERMES AGENT

Hermes is a:

# FIRST-CLASS EXTERNAL AGENT RUNTIME

Before implementing Hermes:

1. inspect actual Hermes repository
2. inspect documentation
3. inspect installation
4. inspect runtime
5. inspect CLI
6. inspect SDK
7. inspect APIs
8. inspect tools
9. inspect MCP support
10. inspect state management
11. inspect authentication
12. inspect security model

Do not invent Hermes functionality.

Create:

docs/hermes/HERMES_INTEGRATION.md

---

# 29. HERMES ADAPTER

Create:

packages/axiom-hermes/

Potential structure:

packages/axiom-hermes/
├── adapter/
├── client/
├── capabilities/
├── tools/
├── security/
└── tests/

The adapter translates between:

Cortex Ledger AI Execution Interface

and

Actual Hermes Interface.

---

# 30. AGENT BACKEND INTERFACE

Create a common backend abstraction.

Conceptually:

class AgentBackend:

    async def execute(self, request):
        ...

    async def capabilities(self):
        ...

    async def health(self):
        ...

Potential implementations:

- AxiomNativeBackend
- HermesBackend
- FutureExternalAgentBackend

---

# 31. TOOL REGISTRY

Cortex Ledger AI must maintain a centralized Tool Registry.

Each tool should eventually have:

- name
- description
- input schema
- output schema
- capabilities
- permissions
- risk level
- handler
- audit configuration

Example:

tool:
    name: create_schedule
    category: workforce
    risk_level: high
    permission: schedule.write

---

# 32. TOOL ACCESS CONTROL

Agents do not automatically receive every tool.

Workflow:

Agent
 ↓
Capability Requirement
 ↓
Tool Discovery
 ↓
Permission Check
 ↓
Budget Check
 ↓
Risk Check
 ↓
Tool Granted
 ↓
Execution
 ↓
Audit

This applies to:

- Cortex Ledger AI agents
- Hermes
- future external runtimes

---

# 33. MCP

MCP is a first-class interoperability layer.

Architecture:

Agent
 ↓
Cortex Ledger AI Tool Registry
 ↓
MCP Client
 ↓
MCP Server
 ↓
External System

Cortex Ledger AI should eventually support:

- consuming MCP servers
- exposing Cortex Ledger AI capabilities through MCP
- mapping MCP tools into Cortex Ledger AI permissions
- auditing MCP calls

---

# 34. GRAPHIFY + MCP

Graphify may expose graph capabilities through MCP depending on the actual installed version and integration path.

Claude Code must inspect and validate the current implementation before relying on MCP.

If Graphify MCP is available:

Graphify
 ↓
MCP
 ↓
Cortex Ledger AI Knowledge Gateway

If direct SDK/CLI integration is more appropriate:

Graphify
 ↓
Graphify Adapter
 ↓
Cortex Ledger AI Knowledge Gateway

Do not assume one integration path.

---

# 35. POLICY ENGINE

The model is not the authority.

The agent is not the authority.

Hermes is not the authority.

Graphify is not the authority.

# CORTEX LEDGER AI POLICY ENGINE IS THE AUTHORITY.

Every sensitive action must pass through policy.

---

# 36. RISK LEVELS

Support:

LOW
MEDIUM
HIGH
CRITICAL

Examples:

Web search
    LOW

Database read
    LOW

Draft content
    LOW

Send email
    MEDIUM

Modify schedule
    HIGH

Issue payment
    HIGH

Delete data
    CRITICAL

Production deployment
    CRITICAL

---

# 37. HUMAN APPROVAL

High-risk actions require human approval when configured.

Workflow:

Agent
 ↓
Proposed Action
 ↓
Policy Engine
 ↓
Risk Assessment
 ↓
Approval Required
 ↓
Human
 ↓
Approve / Reject
 ↓
Execution
 ↓
Verification
 ↓
Audit

This applies regardless of whether the request originated from:

- Cortex Ledger AI
- Claude
- Hermes
- another agent
- an MCP workflow

---

# 38. MEMORY

Cortex Ledger AI memory should support:

Task Memory
Working Memory
Long-Term Memory
Business Knowledge

Memory must include:

- tenant
- scope
- owner
- permissions
- retention
- source

Do not automatically store everything.

---

# 39. AGENT MEMORY ISOLATION

Agents should not automatically see another agent's memory.

Cross-agent memory access must be explicitly authorized.

Hermes does not automatically receive access to all Cortex Ledger AI memory.

---

# 40. OBSERVABILITY

Every meaningful execution must generate a trace.

Track:

- execution ID
- tenant ID
- user ID
- agent ID
- parent agent ID
- backend
- model
- task
- start time
- end time
- token usage
- estimated cost
- tool calls
- agent calls
- knowledge queries
- approvals
- policy decisions
- errors
- result
- evaluation

For Graphify operations, track:

- knowledge query
- graph/project identifier
- query scope
- nodes accessed
- relevant relationships
- execution correlation ID

---

# 41. AGENT GRAPH

Cortex Ledger AI should eventually visualize execution as a graph.

Example:

                 USER
                  │
                  ↓
            CORTEX LEDGER AI DIRECTOR
                  │
       ┌──────────┼──────────┐
       ↓          ↓          ↓
    Agent 17   Hermes     Agent 201
       │          │          │
       │          ↓          │
       │      Agent Gateway  │
       │          │          │
       └──────────┼──────────┘
                  ↓
              SYNTHESIS
                  ↓
                RESULT

---

# 42. KNOWLEDGE GRAPH

Cortex Ledger AI should separately visualize knowledge relationships.

Example:

             Authentication
                   │
        ┌──────────┼──────────┐
        ↓          ↓          ↓
     API Route   Service    Database
        │          │          │
        ↓          ↓          ↓
     Middleware  Function   Schema
                   │
                   ↓
                 Tests

This is distinct from the execution graph.

---

# 43. GRAPHIFY KNOWLEDGE GRAPH VS CORTEX LEDGER AI EXECUTION GRAPH

Keep these separate.

GRAPHIFY:

"What is connected to what in the knowledge domain?"

CORTEX LEDGER AI EXECUTION GRAPH:

"What did the agents do?"

Eventually Cortex Ledger AI may correlate them.

Example:

Agent Execution
      │
      ↓
Graphify Query
      │
      ↓
Authentication Service
      │
      ↓
Affected Files
      │
      ↓
Tool Execution
      │
      ↓
Test Results

This creates a powerful trace of:

knowledge → reasoning → execution → verification.

---

# 44. AGENT EVALUATION

Evaluate:

MODELS

- accuracy
- latency
- cost
- reliability

AGENTS

- task success
- tool selection
- tool accuracy
- delegation quality
- safety

AGENT TEAMS

- coordination
- redundancy
- communication
- final result

HERMES

- task success
- tool use
- policy compliance
- agent invocation
- cost
- latency
- reliability

KNOWLEDGE

- retrieval relevance
- graph query correctness
- grounding
- source traceability

---

# 45. AGENT PERFORMANCE MEMORY

Track actual performance.

Example:

Agent:
Financial Analyst

Tasks:
142

Success Rate:
91%

Average Latency:
14.2 seconds

Average Cost:
$0.08

Tool Accuracy:
96%

Policy Violations:
0

These values must be measured.

Never fabricate metrics.

---

# 46. SECURITY

Design for:

- authentication
- authorization
- tenant isolation
- least privilege
- prompt injection
- indirect prompt injection
- tool authorization
- data exfiltration
- agent escalation
- secret management
- audit logging
- rate limits
- sandboxing
- knowledge access control

---

# 47. SANDBOXING

External agents should operate inside controlled environments where appropriate.

Potential technologies:

- Docker
- restricted subprocesses
- ephemeral containers
- restricted filesystem
- restricted network

Never provide unrestricted:

- root
- sudo
- host filesystem
- production credentials
- network access

unless explicitly required and secured.

---

# 48. DATABASE

Preferred:

PostgreSQL
Supabase

Potential tables:

organizations
users
agents
agent_capabilities
agent_backends
agent_permissions
agent_budgets
agent_invocations
agent_relationships
tools
tool_permissions
tasks
executions
execution_events
approvals
memory
documents
knowledge_sources
knowledge_queries
evaluations
evaluation_runs
security_events

Build incrementally.

---

# 49. REDIS

Use Redis where appropriate for:

- queues
- temporary state
- locks
- caching
- streaming

Do not introduce Redis where PostgreSQL is sufficient.

---

# 50. FRONTEND

Use:

Next.js
React
TypeScript
Tailwind CSS

The interface should feel like:

# AI OPERATIONS COMMAND CENTER

Not a generic chatbot.

Core views:

Dashboard
Agents
Agent Fabric
Agent Registry
Agent Teams
Agent Runs
Execution Graph
Knowledge Graph
Graphify
Knowledge Explorer
Execution Trace
Tools
MCP
Backends
Approvals
Memory
Evaluations
Security
Settings

---

# 51. KNOWLEDGE FABRIC UI

The dashboard should eventually allow:

- repository selection
- Graphify status
- knowledge graph visualization
- architecture exploration
- node search
- dependency exploration
- path tracing
- impact analysis
- documentation exploration
- graph queries
- knowledge-to-execution correlation

---

# 52. AGENT FABRIC UI

The dashboard should eventually allow:

- search 237 agents
- filter by capability
- view profile
- view tools
- view permissions
- view backend
- view performance
- view previous runs
- invoke agent
- create teams
- view relationships

---

# 53. REPOSITORY STRUCTURE

Use this structure unless inspection reveals an existing architecture that should be preserved.

axiom-os/
│
├── CLAUDE.md
├── README.md
├── LICENSE
├── .env.example
├── .gitignore
│
├── apps/
│   ├── api/
│   │   └── axiom_api/
│   ├── dashboard/
│   │   └── ...
│   └── playground/
│       └── ...
│
├── packages/
│   │
│   ├── axiom-core/
│   │   ├── agents/
│   │   ├── orchestration/
│   │   ├── tasks/
│   │   ├── execution/
│   │   ├── models/
│   │   ├── backends/
│   │   ├── routing/
│   │   ├── tools/
│   │   ├── memory/
│   │   ├── permissions/
│   │   ├── policies/
│   │   ├── budgets/
│   │   ├── approvals/
│   │   ├── evaluation/
│   │   └── observability/
│   │
│   ├── axiom-agent-fabric/
│   │   ├── registry/
│   │   ├── discovery/
│   │   ├── router/
│   │   ├── invocation/
│   │   ├── profiles/
│   │   ├── teams/
│   │   ├── permissions/
│   │   ├── budgets/
│   │   └── performance/
│   │
│   ├── axiom-knowledge/
│   │   ├── gateway/
│   │   ├── models/
│   │   ├── permissions/
│   │   ├── queries/
│   │   └── tests/
│   │
│   ├── axiom-graphify/
│   │   ├── adapter/
│   │   ├── client/
│   │   ├── knowledge/
│   │   ├── indexing/
│   │   ├── queries/
│   │   ├── permissions/
│   │   ├── models/
│   │   └── tests/
│   │
│   ├── axiom-hermes/
│   │   ├── adapter/
│   │   ├── client/
│   │   ├── capabilities/
│   │   ├── tools/
│   │   ├── security/
│   │   └── tests/
│   │
│   ├── axiom-mcp/
│   │   ├── clients/
│   │   ├── servers/
│   │   ├── adapters/
│   │   └── permissions/
│   │
│   ├── axiom-anthropic/
│   │   ├── client/
│   │   ├── adapter/
│   │   └── tests/
│   │
│   ├── axiom-db/
│   │   ├── models/
│   │   ├── migrations/
│   │   └── repositories/
│   │
│   └── axiom-sdk/
│
├── agents/
│   ├── registry/
│   ├── native/
│   ├── profiles/
│   ├── examples/
│   └── system/
│
├── knowledge/
│   ├── graphify/
│   ├── schemas/
│   ├── sources/
│   └── queries/
│
├── integrations/
│   ├── anthropic/
│   ├── hermes/
│   ├── graphify/
│   ├── github/
│   ├── supabase/
│   └── postgres/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── agent/
│   ├── agent_fabric/
│   ├── knowledge/
│   ├── graphify/
│   ├── hermes/
│   ├── mcp/
│   ├── evaluation/
│   ├── security/
│   └── end_to_end/
│
├── docs/
│   ├── architecture/
│   ├── agents/
│   ├── agent-fabric/
│   ├── knowledge/
│   ├── graphify/
│   ├── backends/
│   ├── hermes/
│   ├── mcp/
│   ├── security/
│   └── evaluation/
│
├── infrastructure/
│   ├── docker/
│   ├── github/
│   └── deployment/
│
└── scripts/
    ├── dev/
    ├── test/
    ├── evaluation/
    ├── security/
    ├── agents/
    └── knowledge/

---

# 54. TECHNOLOGY STACK

Backend:

Python
FastAPI
Pydantic
asyncio

Frontend:

TypeScript
Next.js
React
Tailwind CSS

AI:

Anthropic
Claude

External Agent Runtime:

Hermes Agent

Knowledge:

Graphify

Agent Protocol:

MCP

Database:

PostgreSQL
Supabase

Queue / Cache:

Redis when required

Infrastructure:

Docker
Docker Compose
GitHub Actions

---

# 55. CLAUDE CODE ENGINEERING RULES

Claude Code must follow:

INSPECT
 ↓
UNDERSTAND
 ↓
ARCHITECT
 ↓
PLAN
 ↓
IMPLEMENT
 ↓
TEST
 ↓
EVALUATE
 ↓
SECURE
 ↓
DOCUMENT
 ↓
REFACTOR

Never immediately start rewriting the repository.

---

# 56. NEVER

Never:

- invent Hermes APIs
- invent Graphify APIs
- invent MCP capabilities
- fabricate agent capabilities
- fabricate benchmark results
- fabricate performance metrics
- hard-code secrets
- bypass policy
- bypass approval
- give Hermes unrestricted access
- give agents unrestricted tool access
- expose all 237 agents to every context
- create unlimited recursive calls
- silently rewrite architecture
- rewrite the repository unnecessarily
- claim an integration works without testing
- treat Graphify as merely a visualization
- treat the 237 agents as unrelated applications

---

# 57. ALWAYS

Always:

- inspect before modifying
- use real APIs
- validate integrations
- write tests
- enforce permissions
- log important actions
- maintain tenant boundaries
- maintain execution traces
- document decisions
- record limitations
- use environment variables for secrets
- create reproducible setup instructions
- preserve existing source-of-truth agent definitions
- distinguish knowledge from memory
- distinguish models from agent runtimes
- distinguish control plane from execution plane

---

# 58. PROJECT 1 — CORTEX LEDGER AI MVP

The first objective is to prove:

> Cortex Ledger AI can orchestrate a frontier model, a real external agent runtime, a controlled library of specialized agents, a knowledge graph, tools, MCP services, memory, policy, approvals, and execution traces.

Required MVP components:

Cortex Ledger AI Runtime
Model Gateway
Hermes Adapter
Agent Fabric
Agent Registry
Agent Discovery
Agent Router
Agent Invocation Gateway
Knowledge Gateway
Graphify Adapter
Tool Registry
MCP Client
Permissions
Budgets
Policy Engine
Human Approval
Task Memory
Execution Tracing
Evaluation
Dashboard

---

# 59. FIRST DEMO — KNOWLEDGE-GROUNDED RESEARCH

User:

"Research this software repository and explain how authentication works."

Cortex Ledger AI:

Receive Task
 ↓
Create Execution
 ↓
Classify Task
 ↓
Knowledge Query
 ↓
Graphify
 ↓
Identify Authentication Architecture
 ↓
Discover Relevant Agents
 ↓
Select Backend
 ↓
Permission Check
 ↓
Execute
 ↓
Verify
 ↓
Evaluate
 ↓
Audit
 ↓
Return Result

---

# 60. SECOND DEMO — HERMES

After inspecting the actual Hermes implementation, create a meaningful Hermes workflow.

Potential architecture:

User
 ↓
Cortex Ledger AI
 ↓
Task Planner
 ↓
Hermes
 ↓
Cortex Ledger AI Agent Gateway
 ↓
Specialized Agent
 ↓
Authorized Tools
 ↓
Knowledge Gateway
 ↓
Graphify
 ↓
Result
 ↓
Cortex Ledger AI Verification
 ↓
Final Result

The actual workflow must be based on Hermes's real capabilities.

---

# 61. THIRD DEMO — HERMES ACCESSING AGENT FABRIC

Key portfolio demonstration:

User:
"Develop a go-to-market strategy."

              ↓

Cortex Ledger AI Director
              ↓
         Hermes Agent
              ↓
     Cortex Ledger AI Agent Gateway
              ↓
       Agent Discovery
              ↓
 ┌────────────┼────────────┐
 ↓            ↓            ↓
Market      Finance      Marketing
Agent       Agent        Agent
 ↓            ↓            ↓
Research    Forecast     Campaign
              ↓
        Results Returned
              ↓
            Hermes
              ↓
          Synthesis
              ↓
            Cortex Ledger AI
              ↓
        Final Response

Every invocation is:

- authorized
- budgeted
- traced
- auditable

---

# 62. FOURTH DEMO — GRAPHIFY-GROUNDED AGENT

Demonstrate:

User
 ↓
Cortex Ledger AI
 ↓
Graphify
 ↓
Architecture Understanding
 ↓
Agent Discovery
 ↓
Software Engineering Agent
 ↓
Claude/Hermes
 ↓
Authorized Tool
 ↓
Repository Change
 ↓
Tests
 ↓
Graphify Re-index
 ↓
Impact Analysis
 ↓
Evaluation
 ↓
Approval
 ↓
Result

This demonstrates that agents can reason over actual system structure instead of blindly searching files.

---

# 63. FIFTH DEMO — AGENT TEAM

Cortex Ledger AI dynamically creates:

Business Strategy Director
        │
        ├── Market Research
        ├── Financial Analyst
        ├── Marketing Strategist
        ├── Sales Strategist
        └── Operations Strategist

Show:

- why each agent was selected
- capabilities
- permissions
- budgets
- tools
- knowledge accessed
- execution status
- results
- final synthesis

---

# 64. SIXTH DEMO — HUMAN APPROVAL

Create a high-risk tool:

modify_business_record

Workflow:

Agent
 ↓
Proposed Action
 ↓
Policy Engine
 ↓
HIGH RISK
 ↓
Approval Required
 ↓
Human Approves
 ↓
Execute
 ↓
Verify
 ↓
Audit

Test with:

- Cortex Ledger AI native agent
- Hermes
- agent-to-agent delegation

---

# 65. SEVENTH DEMO — CROSS-BACKEND ORCHESTRATION

Demonstrate:

Cortex Ledger AI Director
      ↓
Claude
      ↓
Planning
      ↓
Graphify / Knowledge Fabric
      ↓
Agent Fabric
      ↓
Specialized Agent
      ↓
Hermes
      ↓
External Execution
      ↓
Claude
      ↓
Synthesis
      ↓
Evaluation

Every backend must have a legitimate role.

Do not use multiple systems merely for appearance.

---

# 66. AGENT REGISTRY MVP

Version 1 must support:

Create Agent
Register Agent
Get Agent
List Agents
Search Agents
Filter by Capability
Get Capabilities
Get Permissions
Invoke Agent
Track Invocation

Then import the existing agent library.

---

# 67. AGENT NORMALIZATION

Convert the existing agents into normalized Cortex Ledger AI representations.

Potential fields:

agent_id
name
description
category
capabilities
instructions
backend
tools
permissions
risk_level
budget
memory_scope
status
version
metadata

Preserve original definitions.

Do not destroy source information.

---

# 68. AGENT VERSIONING

Track:

version
created_at
updated_at
author
changes
evaluation_results

This enables regression testing.

---

# 69. AGENT LIFECYCLE

Support:

DRAFT
TESTING
ACTIVE
PAUSED
DEPRECATED
ARCHIVED

Do not allow untested agents to automatically perform high-risk production actions.

---

# 70. GRAPHIFY KNOWLEDGE LIFECYCLE

Support:

UNINDEXED
INDEXING
INDEXED
STALE
UPDATING
ERROR

Cortex Ledger AI should know whether knowledge is current before relying on it.

---

# 71. KNOWLEDGE FRESHNESS

Cortex Ledger AI must eventually track:

- graph generation time
- source commit
- indexed files
- stale state
- last update
- indexing errors

Do not silently treat stale knowledge as current.

---

# 72. GRAPHIFY RE-INDEXING

When code changes:

Change
 ↓
Graphify Update
 ↓
Knowledge Graph Refresh
 ↓
Impact Analysis
 ↓
Verification

Where supported, use incremental/update mechanisms rather than rebuilding everything unnecessarily.

---

# 73. AGENT EVALUATION

Every important agent should eventually be evaluated.

Example:

Agent
 ↓
Benchmark Tasks
 ↓
Execution
 ↓
Scoring
 ↓
Performance Record

Metrics:

Task Success
Accuracy
Tool Accuracy
Delegation Quality
Latency
Cost
Safety
Policy Violations

---

# 74. KNOWLEDGE EVALUATION

Evaluate:

- query relevance
- graph grounding
- source traceability
- architecture accuracy
- dependency accuracy
- impact-analysis accuracy

Never assume a knowledge graph is correct simply because it exists.

---

# 75. EVALUATION BENCHMARK

Create an initial benchmark of at least:

20 TASKS

Include:

Research
Analysis
Planning
Marketing
Finance
Operations
Tool Use
Agent Delegation
Hermes Delegation
Knowledge Queries
Graphify Queries
Human Approval

Measure actual results.

Never fabricate scores.

---

# 76. MILESTONE 0 — REPOSITORY AUDIT

Before coding:

Inspect:

Repository
Files
Dependencies
Python
Node
Package Managers
Database
Environment
Tests
Documentation
Git

Do not modify code during initial audit.

Deliver:

docs/ARCHITECTURE_AUDIT.md

---

# 77. MILESTONE 1 — GRAPHIFY AUDIT

Inspect actual Graphify repository.

Determine:

Repository
Architecture
Language
Framework
Installation
CLI
API
SDK
Graph Model
Indexing
Parsing
Queries
MCP
Visualization
Security
Licensing

Deliver:

docs/graphify/GRAPHIFY_AUDIT.md

---

# 78. MILESTONE 2 — HERMES RESEARCH

Inspect actual Hermes implementation.

Determine:

Installation
Runtime
API
CLI
SDK
Tools
MCP
Capabilities
State
Authentication
Security
Execution Model

Deliver:

docs/hermes/HERMES_INTEGRATION.md

---

# 79. MILESTONE 3 — AGENT LIBRARY AUDIT

Locate existing 237-agent library.

Determine:

Where agents are stored
Format
Agent count
Categories
Descriptions
Capabilities
Tools
Dependencies
Duplicates
Incomplete agents

Deliver:

docs/agent-fabric/AGENT_LIBRARY_AUDIT.md

---

# 80. MILESTONE 4 — ARCHITECTURE DESIGN

Produce:

docs/IMPLEMENTATION_PLAN.md

Must show:

Cortex Ledger AI
Agent Fabric
Knowledge Fabric
Graphify
Execution Engine
Claude
Hermes
Tools
MCP
Memory
Policy
Approvals
Evaluation
Dashboard

---

# 81. MILESTONE 5 — AGENT NORMALIZATION

Build:

Existing Agents
 ↓
Normalization Pipeline
 ↓
Cortex Ledger AI Registry

Do not manually recreate the agent library unless necessary.

---

# 82. MILESTONE 6 — FOUNDATION

Build:

Configuration
Logging
Database
Testing
Environment Management

---

# 83. MILESTONE 7 — MODEL GATEWAY

Implement:

Anthropic Backend

Then implement other providers only when needed.

---

# 84. MILESTONE 8 — KNOWLEDGE GATEWAY

Implement:

Knowledge Interface
Graphify Adapter
Knowledge Permissions
Query Execution
Knowledge Tracing

---

# 85. MILESTONE 9 — AGENT RUNTIME

Implement:

Agent
Task
Execution
Result

---

# 86. MILESTONE 10 — AGENT FABRIC

Implement:

Registry
Profiles
Discovery
Router
Invocation Gateway
Permissions
Budgets

---

# 87. MILESTONE 11 — TOOL REGISTRY

Implement:

Register Tool
Discover Tool
Authorize Tool
Execute Tool
Audit Tool

---

# 88. MILESTONE 12 — MCP

Implement:

MCP Client
Tool Discovery
Permission Mapping
Tool Execution
Audit

---

# 89. MILESTONE 13 — HERMES INTEGRATION

Implement only after actual Hermes inspection:

Hermes Adapter
Capability Discovery
Task Execution
Agent Gateway Access
Tool Gateway Access
Permission Enforcement
Budget Enforcement
Execution Trace
Error Handling

---

# 90. MILESTONE 14 — MEMORY

Implement:

Task Memory
Agent Memory
Execution State
Basic Retrieval
Permission Boundaries

---

# 91. MILESTONE 15 — POLICY

Implement:

Permissions
Risk Levels
Authorization
Denial
Budgets
Rate Limits
Audit

---

# 92. MILESTONE 16 — HUMAN APPROVAL

Implement:

Approval Request
Approval State
Approve
Reject
Execute
Verify
Audit

---

# 93. MILESTONE 17 — OBSERVABILITY

Implement:

Execution Traces
Agent Graph
Knowledge Queries
Knowledge Graph References
Logs
Metrics
Latency
Token Usage
Cost Estimation
Agent Invocations
Tool Calls
Policy Decisions

---

# 94. MILESTONE 18 — DASHBOARD

Build:

Dashboard
Agent Registry
Agent Search
Agent Profile
Agent Teams
Agent Runs
Execution Graph
Knowledge Graph
Graphify Explorer
Execution Trace
Tools
MCP
Backends
Approvals
Memory
Evaluations
Security

---

# 95. MILESTONE 19 — EVALUATION

Build:

Benchmark Tasks
Evaluation Runner
Scoring
Regression Testing
Agent Performance
Backend Performance
Knowledge Performance
Hermes Performance

---

# 96. MILESTONE 20 — SECURITY

Run:

Prompt Injection Tests
Agent Authorization Tests
Tool Authorization Tests
Budget Tests
Memory Isolation Tests
Tenant Isolation Tests
Knowledge Isolation Tests
Hermes Security Tests
Graphify Access Tests
Approval Bypass Tests
Recursive Delegation Tests

---

# 97. MILESTONE 21 — PORTFOLIO RELEASE

Produce:

README.md
ARCHITECTURE.md
SECURITY.md
EVALUATION.md
HERMES_INTEGRATION.md
GRAPHIFY_INTEGRATION.md
AGENT_FABRIC.md
KNOWLEDGE_FABRIC.md
API Documentation
Architecture Diagrams
Screenshots
Demo Video
Setup Instructions

---

# 98. DEFINITION OF DONE

Cortex Ledger AI MVP is complete only when:

- Cortex Ledger AI runtime works
- Anthropic integration works
- Hermes integration works
- Agent Registry works
- Existing agent library can be represented
- Agent Discovery works
- Agent Router works
- Agent Invocation Gateway works
- Agent permissions work
- Agent budgets work
- Agent-to-agent calls are controlled
- Hermes cannot bypass Cortex Ledger AI
- Graphify integration works
- Knowledge Gateway works
- Knowledge permissions work
- Tool Registry works
- MCP works
- Memory works
- Policy Engine works
- Human Approval works
- Execution tracing works
- Knowledge queries are traceable
- Agent graph works
- Knowledge graph is accessible
- Dashboard works
- Evaluation system works
- Security tests exist
- Automated tests pass
- Documentation exists
- Clean installation works
- Portfolio demo works

---

# 99. BUSINESS OPERATIONS WILL CONSUME CORTEX LEDGER AI

Once Cortex Ledger AI is stable, Business Operations should be built on top of it.

Architecture:

                 BUSINESS OPERATIONS
                       │
                       ↓
                   CORTEX LEDGER AI
                       │
        ┌──────────────┼──────────────┐
        ↓              ↓              ↓
   AGENT FABRIC   KNOWLEDGE FABRIC  EXECUTION
        │              │              │
   237 Agents       Graphify        Claude
   Capabilities     Knowledge       Hermes
   Permissions      Graph            Native
   Tools            Context         Tools/MCP
        │              │              │
        └──────────────┼──────────────┘
                       │
                 Business Systems

Business Operations must not recreate:

- agent orchestration
- model routing
- knowledge orchestration
- memory
- permissions
- approvals
- evaluation
- observability

Cortex Ledger AI provides these capabilities.

---

# 100. FUTURE PROJECT — CORTEX LEDGER AI SWE

Graphify becomes a core component of Cortex Ledger AI SWE.

Workflow:

Repository
 ↓
Graphify
 ↓
Repository Understanding
 ↓
Architecture Analysis
 ↓
Impact Analysis
 ↓
Agent Selection
 ↓
Claude / Hermes
 ↓
Coding
 ↓
Tests
 ↓
Graphify Re-index
 ↓
Architecture Verification
 ↓
Evaluation
 ↓
Human Approval
 ↓
Git / Pull Request

This project should demonstrate that Cortex Ledger AI can reason about real software systems rather than simply generate code.

---

# 101. FUTURE PROJECT — CORTEX LEDGER AI SENTINEL

Incident
 ↓
Detection
 ↓
Graphify
 ↓
Architecture Understanding
 ↓
Investigation
 ↓
Logs
 ↓
Git
 ↓
Deployment History
 ↓
Root Cause
 ↓
Remediation
 ↓
Approval
 ↓
Verification

---

# 102. FUTURE PROJECT — CORTEX LEDGER AI EVAL

Standalone evaluation platform for:

Models
Agents
Agent Teams
Tools
MCP
External Agents
Hermes
Cortex Ledger AI
Knowledge Systems

---

# 103. FUTURE PROJECT — CORTEX LEDGER AI GUARD

Security infrastructure for:

Prompt Injection
Indirect Injection
Data Exfiltration
Tool Abuse
Permission Escalation
Agent Isolation
Knowledge Isolation
Secrets
Audit
Policy

---

# 104. PORTFOLIO POSITIONING

The completed Cortex Ledger AI project should demonstrate:

Frontier Model Integration
Agent Runtime Architecture
Multi-Agent Orchestration
External Agent Integration
Hermes Integration
Agent Registry Design
Agent Discovery
Agent Routing
Agent-to-Agent Communication
Tool Calling
MCP
Knowledge Graphs
Graphify Integration
Codebase Intelligence
Memory
RAG
Human-in-the-Loop
Policy Enforcement
Budget Controls
Agent Evaluation
AI Security
Observability
Python
FastAPI
TypeScript
Next.js
PostgreSQL
Supabase
Redis
Docker
CI/CD

The portfolio story:

> "I engineered an agentic AI operating layer capable of orchestrating frontier models, external agent runtimes, and a registry of specialized business agents through controlled tools, MCP, permissions, budgets, knowledge graphs, memory, human approval, evaluation, and observability."

The deeper engineering story:

> "Cortex Ledger AI separates who performs work, what the system knows, and how work is executed."

That means:

AGENT FABRIC
=
WHO

KNOWLEDGE FABRIC
=
WHAT

EXECUTION ENGINE
=
HOW

---

# 105. EXACT STARTUP INSTRUCTIONS FOR CLAUDE CODE

When Claude Code starts:

## STEP 1 — STOP AND AUDIT

Do not immediately write application code.

Inspect the repository.

---

## STEP 2 — IDENTIFY THE EXISTING SYSTEM

Document:

Architecture
Applications
Dependencies
Python Version
Node Version
Package Manager
Database
Environment
Tests
Documentation
Git

---

## STEP 3 — LOCATE THE 237 AGENTS

Find the existing agency-agent library.

Determine:

File locations
Format
Agent count
Agent names
Categories
Descriptions
Instructions
Tools
Dependencies
Metadata

Count the agents programmatically.

Do not assume the count.

---

## STEP 4 — INSPECT GRAPHIFY

Locate the Graphify integration/repository.

If the repository is not already present, inspect the documented Graphify repository and determine the appropriate integration strategy.

Inspect:

Architecture
Installation
CLI
SDK/API
Graph Model
Indexing
Parsing
Queries
MCP
Visualization
Security
Licensing

Do not invent functionality.

---

## STEP 5 — INSPECT HERMES

Inspect the actual Hermes Agent implementation and documentation.

Determine:

Architecture
Installation
Runtime
API
CLI
SDK
Tools
MCP
Capabilities
State
Security
Integration Options

Do not guess.

---

## STEP 6 — CREATE AUDIT DOCUMENTS

Create:

docs/ARCHITECTURE_AUDIT.md

docs/graphify/GRAPHIFY_AUDIT.md

docs/hermes/HERMES_INTEGRATION.md

docs/agent-fabric/AGENT_LIBRARY_AUDIT.md

docs/IMPLEMENTATION_PLAN.md

---

## STEP 7 — PROPOSE FINAL ARCHITECTURE

Before major implementation, show how:

Cortex Ledger AI
Agent Fabric
237 Agents
Knowledge Fabric
Graphify
Execution Engine
Claude
Hermes
Tools
MCP
Memory
Policy
Approvals
Evaluation
Dashboard

fit together.

---

# 106. FIRST FUNCTIONAL TARGET

The first meaningful end-to-end workflow:

USER
 ↓
CORTEX LEDGER AI
 ↓
TASK CLASSIFICATION
 ↓
KNOWLEDGE QUERY
 ↓
GRAPHIFY
 ↓
AGENT DISCOVERY
 ↓
AGENT SELECTION
 ↓
BACKEND SELECTION
 ↓
TOOL DISCOVERY
 ↓
PERMISSION CHECK
 ↓
EXECUTION
 ↓
VERIFICATION
 ↓
EVALUATION
 ↓
AUDIT
 ↓
RESULT

Then extend to:

USER
 ↓
CORTEX LEDGER AI
 ↓
HERMES
 ↓
CORTEX LEDGER AI AGENT GATEWAY
 ↓
237-AGENT REGISTRY
 ↓
SPECIALIZED AGENT
 ↓
KNOWLEDGE GATEWAY
 ↓
GRAPHIFY
 ↓
AUTHORIZED TOOL
 ↓
RESULT
 ↓
HERMES
 ↓
CORTEX LEDGER AI
 ↓
VERIFICATION
 ↓
RESULT

---

# 107. MOST IMPORTANT ARCHITECTURAL PRINCIPLE

The 237 agents are not 237 applications.

They are members of:

# CORTEX LEDGER AI AGENT FABRIC

The Fabric provides:

Identity
Capabilities
Tools
Permissions
Budgets
Memory
Routing
Execution
Evaluation
Observability
Versioning

---

# 108. MOST IMPORTANT KNOWLEDGE PRINCIPLE

Graphify is not simply a visualization tool.

It becomes part of:

# CORTEX LEDGER AI KNOWLEDGE FABRIC

Graphify provides structured knowledge that agents can query before acting.

The goal is:

Raw Repository
 ↓
Graphify
 ↓
Structured Knowledge
 ↓
Cortex Ledger AI Knowledge Gateway
 ↓
Agent Context
 ↓
Reasoning
 ↓
Execution
 ↓
Verification

---

# 109. MOST IMPORTANT HERMES PRINCIPLE

Hermes is an execution capability.

Hermes is not the owner of Cortex Ledger AI.

Cortex Ledger AI remains the control plane.

                    CORTEX LEDGER AI
                 CONTROL PLANE
                      │
       ┌──────────────┼──────────────┐
       ↓              ↓              ↓
   Agent Fabric   Knowledge       Execution
                   Fabric           Engine
       │              │              │
   237 Agents      Graphify        Claude
       │              │            Hermes
       │              │            Native
       └──────────────┼──────────────┘
                      │
                    Tools
                      │
                     MCP
                      │
              Business Systems

---

# 110. FINAL MISSION

Claude Code:

You are building the foundation for an AI engineering portfolio.

Do not optimize for the number of features.

Optimize for:

Correct Architecture
Real Integrations
Reliable Execution
Security
Evaluation
Observability
Knowledge Grounding
Scalability
Demonstrable Engineering

The 237-agent library should become a real Agent Fabric.

Graphify should become the foundation of the Knowledge Fabric.

Hermes should become a real external agent runtime.

Claude should become a frontier-model backend.

MCP should become the interoperability layer.

The Policy Engine should remain the authority.

The Evaluation System should measure whether the system actually works.

The Dashboard should make the entire system visible.

The final architecture:

                         CORTEX LEDGER AI
                            │
       ┌────────────────────┼────────────────────┐
       │                    │                    │
       ▼                    ▼                    ▼
 AGENT FABRIC          KNOWLEDGE FABRIC      EXECUTION ENGINE
       │                    │                    │
       │                  GRAPHIFY                │
       │                    │                    │
       │              ┌─────┼─────┐              │
       │              │     │     │              │
       │            Code   Deps   Docs            │
       │              │     │     │              │
       │              └─────┼─────┘              │
       │                    │                    │
       │                    │              ┌─────┼──────┐
       │                    │              │     │      │
       │                    │            Claude Hermes Native
       │                    │                    │
   237 Agents              │                    │
   Capabilities             │                    │
   Permissions              │                    │
   Tools                    │                    │
       │                    │                    │
       └────────────────────┼────────────────────┘
                            │
                    BUSINESS OPERATIONS

The ultimate engineering thesis:

> AI engineering is not just calling an LLM.

> It is engineering the systems around intelligence that allow agents to understand their environment, discover capabilities, reason over structured knowledge, collaborate, execute actions, verify outcomes, and operate safely at scale.

START HERE:

AUDIT
  ↓
LOCATE 237 AGENTS
  ↓
INSPECT GRAPHIFY
  ↓
INSPECT HERMES
  ↓
ARCHITECT THREE-PILLAR SYSTEM
  ↓
BUILD FOUNDATION
  ↓
MODEL GATEWAY
  ↓
KNOWLEDGE GATEWAY
  ↓
GRAPHIFY INTEGRATION
  ↓
AGENT RUNTIME
  ↓
AGENT REGISTRY
  ↓
AGENT DISCOVERY
  ↓
AGENT ROUTER
  ↓
HERMES INTEGRATION
  ↓
TOOLS + MCP
  ↓
POLICY + BUDGETS
  ↓
HUMAN APPROVAL
  ↓
MEMORY
  ↓
OBSERVABILITY
  ↓
EVALUATION
  ↓
SECURITY
  ↓
DASHBOARD
  ↓
PORTFOLIO DEMO

DO NOT SKIP THE AUDIT.

DO NOT INVENT HERMES FUNCTIONALITY.

DO NOT INVENT GRAPHIFY FUNCTIONALITY.

DO NOT GIVE HERMES UNRESTRICTED ACCESS TO THE 237 AGENTS.

DO NOT EXPOSE EVERY AGENT TO EVERY MODEL.

DO NOT GIVE AGENTS UNRESTRICTED TOOL ACCESS.

DO NOT BYPASS CORTEX LEDGER AI PERMISSIONS, BUDGETS, POLICY, OR AUDIT LOGGING.

DO NOT FABRICATE TEST RESULTS.

---

# 111. CORTEX LEDGER AI — CONVERSATIONAL COMMAND INTERFACE

## Purpose

Cortex Ledger AI must not be built as a backend-only AI orchestration system.

It must provide a human-facing conversational command interface that allows a user to communicate with Cortex Ledger AI through:

- Text
- Voice
- Spoken responses
- Execution status
- Agent activity
- Approval requests
- Results
- Follow-up conversation

The user should be able to communicate with Cortex Ledger AI naturally rather than needing to know:

- which agent to use
- which model to use
- which tool to use
- which MCP server to use
- which workflow to execute
- how the Agent Registry works

The user communicates with:

# CORTEX LEDGER AI

Cortex Ledger AI determines what needs to happen internally.

## Architecture

The conversational interface is a separate layer from the core Cortex Ledger AI infrastructure.

Architecture:

```
                         USER
                           │
              ┌────────────┴────────────┐
              │                         │
             TEXT                      VOICE
              │                         │
              │                  Speech-to-Text
              │                         │
              └────────────┬────────────┘
                           │
                           ▼
                CORTEX LEDGER AI COMMAND INTERFACE
                           │
                           ▼
                     ORCHESTRATOR
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
    AGENT FABRIC     KNOWLEDGE FABRIC   EXECUTION ENGINE
          │                │                │
     237 Agents         Graphify        Claude
          │                │             Hermes
          │                │             Native
          │                │             Tools
          │                │             MCP
          └────────────────┼────────────────┘
                           │
                           ▼
                     VERIFICATION
                           │
                           ▼
                      EVALUATION
                           │
                           ▼
                    RESPONSE ENGINE
                           │
                  ┌────────┴────────┐
                  │                 │
                TEXT              VOICE
                  │                 │
                  │            Text-to-Speech
                  │                 │
                  └────────┬────────┘
                           │
                           ▼
                          USER
```

---

BUILD THE FIRST REAL VERSION OF CORTEX LEDGER AI.