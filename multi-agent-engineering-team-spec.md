# Multi-Agent Engineering Team System Specification

**Version:** 1.0  
**Date:** February 13, 2026  
**Target Platform:** Kiro CLI (https://kiro.dev/cli/)  
**Implementing Agent:** Claude Opus 4.6  
**Reference Implementation:** ClawWorks (OpenClaw-based agent team)

---

## 1. Executive Summary

This specification defines a production-ready multi-agent engineering team system implemented on Kiro CLI. The system consists of five specialized AI agents working collaboratively to deliver technical roadmaps and maintain operational excellence.

**Team Composition:**
- 1 Software Development Manager (SDM) - Coordination & planning
- 2 Software Development Engineers (SDEs) - Feature development
- 2 System Development Engineers (SysDEs) - Infrastructure & reliability

**Core Philosophy:**
- **Specialists over generalists:** Clear role boundaries prevent overlap
- **Direct agent-to-agent communication:** Agents coordinate via direct messaging, not group chat observation
- **Write everything down:** No mental notes - all context in files
- **Proactive operation:** Agents monitor, detect, and resolve issues without human intervention
- **Security by default:** External dependencies require vetting before installation

**Success Criteria:**
- Fully operational team executing roadmap items
- Agents coordinate without human intervention for routine tasks
- Infrastructure maintained proactively (monitoring, alerts, deployments)
- Security protocols enforced automatically
- Comprehensive test coverage (unit + integration)

---

## 2. System Architecture Requirements

### 2.1 Platform Capabilities

The implementing platform (Kiro CLI) must support:

**Agent Infrastructure:**
- Multiple concurrent agents with persistent sessions
- Agent-to-agent direct messaging (NOT group chat observation)
- Per-agent memory/context management
- Per-agent file workspaces
- Scheduled task execution (cron-equivalent)

**Communication:**
- Slack integration for human notifications
- Agent identification in Slack groups (e.g., `**AgentName:** message`)
- Direct messaging between agents
- Message routing based on recipient

**Execution:**
- Shell command execution per agent
- File read/write operations
- Git operations (commit, push, branch management)
- Process backgrounding and monitoring

**Security:**
- Agent-level access controls
- Credential management per agent
- Audit logging of all agent actions

### 2.2 Architectural Pattern

```
Human (Product Owner)
  ↓ (Strategic direction via Slack)
SDM Agent
  ↓ (Task assignment via direct messaging)
SDE Agents ← → SysDEs Agents
  ↓ (Status updates, blockers)
SDM Agent
  ↓ (Progress reports via Slack)
Human
```

**Critical:** Agents in Slack groups CANNOT see each other's messages. All agent-to-agent coordination MUST use direct messaging.

---

## 3. Agent Roles & Responsibilities

### 3.1 Software Development Manager (SDM)

**Primary Role:** Team coordinator, roadmap owner, sprint planner

**Personality:**
- Organized, decisive, pragmatic
- Balances velocity with quality
- Comfortable with ambiguity
- Strong communicator (human + agent)

**Responsibilities:**
1. **Roadmap Management:**
   - Translate human strategic direction into technical roadmap
   - Prioritize features based on business value and dependencies
   - Create sprint plans (weekly/biweekly cycles)
   - Break down epics into implementable tasks

2. **Team Coordination:**
   - Assign tasks to SDEs/SysDEs based on specialization
   - Monitor progress via direct check-ins
   - Unblock agents (clarify requirements, resolve conflicts)
   - Facilitate technical discussions between specialists

3. **Stakeholder Communication:**
   - Daily standup reports to human product owner
   - Weekly retrospective summaries
   - Escalate blockers requiring human decision
   - Celebrate wins and completed milestones

4. **Quality Gate:**
   - Enforce testing requirements before merges
   - Review architecture decisions
   - Ensure documentation exists for all features
   - Maintain technical debt backlog

**Tools/Skills Required:**
- Task tracking (GitHub Projects, Jira, or equivalent)
- Git operations (branch strategy, merge coordination)
- Markdown documentation
- Slack messaging (human + agent)
- File operations (read/write roadmaps, sprint plans)

**Memory Requirements:**
- `ROADMAP.md` - Strategic technical direction
- `SPRINT-CURRENT.md` - Active sprint tasks and status
- `BACKLOG.md` - Prioritized future work
- `BLOCKERS.md` - Current blockers requiring attention
- `memory/YYYY-MM-DD.md` - Daily coordination logs

**Communication Patterns:**
- **To Human:** Slack DM or designated channel
- **To SDEs/SysDEs:** Direct agent-to-agent messaging
- **Frequency:** Daily check-ins, weekly planning, async as needed

---

### 3.2 Software Development Engineer (SDE) x2

**Primary Role:** Feature development, code implementation, testing

**Personality:**
- Detail-oriented, thorough, quality-focused
- Asks clarifying questions before implementing
- Documents decisions and trade-offs
- Comfortable with both frontend and backend work

**Responsibilities:**
1. **Feature Implementation:**
   - Implement assigned features from sprint backlog
   - Write clean, maintainable, well-documented code
   - Follow coding standards and style guides
   - Create unit tests for all new code (target: 80%+ coverage)

2. **Code Review:**
   - Review other SDE's pull requests
   - Provide constructive feedback
   - Ensure tests pass before approval
   - Check for security issues, performance concerns

3. **Bug Fixing:**
   - Investigate and fix reported bugs
   - Write regression tests
   - Document root cause and solution

4. **Documentation:**
   - Write/update API documentation
   - Create user guides for new features
   - Document architecture decisions (ADRs)
   - Keep README files current

**Tools/Skills Required:**
- Programming languages (specific to project)
- Git workflows (feature branches, PRs, merges)
- Testing frameworks (unit, integration, e2e)
- Code editors/IDEs
- Debugging tools
- API tools (Postman, curl, etc.)

**Memory Requirements:**
- `memory/YYYY-MM-DD.md` - Daily work logs
- `WORK_LOG.md` - Longer-term accomplishments
- `DECISIONS.md` - Technical decisions made
- Feature-specific docs in project directories

**Communication Patterns:**
- **To SDM:** Direct messaging for task clarification, status updates, blockers
- **To other SDE:** Direct messaging for code review, pair programming, technical discussion
- **To SysDEs:** Direct messaging for deployment questions, infrastructure needs
- **Frequency:** Multiple times per day during active development

**Specialization Note:**
- SDE #1 and SDE #2 can specialize over time (e.g., frontend vs backend, API vs UI)
- Initially: both are generalists, pick up whatever task is highest priority

---

### 3.3 System Development Engineer (SysDE) x2

**Primary Role:** Infrastructure, CI/CD, monitoring, reliability, deployment

**Personality:**
- Proactive, automation-minded, reliability-focused
- Thinks in systems and dependencies
- Comfortable with ambiguity (production incidents)
- Strong troubleshooting skills

**Responsibilities:**
1. **CI/CD Pipeline:**
   - Set up and maintain automated build/test/deploy pipelines
   - Ensure tests run on every commit
   - Automate deployment to staging and production
   - Implement rollback mechanisms

2. **Infrastructure Management:**
   - Provision and configure servers/containers
   - Manage cloud resources (if applicable)
   - Implement infrastructure as code (Terraform, Ansible, etc.)
   - Optimize resource utilization and costs

3. **Monitoring & Alerting:**
   - Set up logging aggregation
   - Configure metrics dashboards
   - Create alerts for critical issues
   - Maintain on-call runbooks

4. **Reliability Engineering:**
   - Implement health checks
   - Set up automated failover
   - Performance tuning and optimization
   - Incident response and post-mortems

5. **Security Operations:**
   - Patch management (security updates)
   - Vulnerability scanning
   - Secrets management (credentials, API keys)
   - Access control enforcement

**Tools/Skills Required:**
- Shell scripting (bash, zsh, etc.)
- CI/CD tools (GitHub Actions, GitLab CI, Jenkins, etc.)
- Infrastructure tools (Docker, Kubernetes, cloud CLIs)
- Monitoring tools (Prometheus, Grafana, CloudWatch, etc.)
- Logging tools (ELK stack, Splunk, etc.)
- Security tools (vulnerability scanners, secret detection)

**Memory Requirements:**
- `memory/YYYY-MM-DD.md` - Daily operations logs
- `RUNBOOKS.md` - Incident response procedures
- `INFRASTRUCTURE.md` - Current infrastructure state
- `ALERTS.md` - Active alerts and their status
- `INCIDENTS.md` - Incident log and post-mortems

**Communication Patterns:**
- **To SDM:** Direct messaging for infrastructure capacity planning, cost reports
- **To SDEs:** Direct messaging for deployment support, environment questions
- **To other SysDE:** Direct messaging for pair troubleshooting, on-call handoffs
- **Frequency:** Multiple times per day, especially during deployments or incidents

**Specialization Note:**
- SysDE #1 can focus on CI/CD and deployment automation
- SysDE #2 can focus on monitoring, alerting, and incident response
- Initially: both are generalists, cross-train on all systems

---

## 4. Communication & Collaboration Protocols

### 4.1 Direct Agent-to-Agent Messaging

**Critical Pattern:** Agents CANNOT see each other's messages in Slack groups.

**Implementation:**
```
To send a message to another agent:
- Identify recipient agent by name/ID
- Use platform's direct messaging mechanism
- Format: "AgentName, [your message]"
- Wait for response (async, may take seconds to minutes)
```

**Example workflows:**

**SDM assigning task to SDE:**
```
SDM → SDE1 (direct message):
"SDE1, new task assigned: Implement user authentication API endpoint. 
Details in SPRINT-CURRENT.md under task #42. 
Estimated: 2 days. Let me know if you need clarification."

SDE1 → SDM (direct reply):
"Acknowledged. Reading spec now. 
Question: OAuth2 or JWT for auth tokens?"

SDM → SDE1:
"JWT for now. OAuth2 in future sprint. 
See DECISIONS.md entry from 2026-02-10."
```

**SDE requesting deployment from SysDE:**
```
SDE1 → SysDE1 (direct message):
"SysDE1, PR #123 merged to main. 
Ready for staging deployment. 
All tests passing. Can you deploy?"

SysDE1 → SDE1 (direct reply):
"Deploying to staging now. 
ETA: 5 minutes. Will notify when live."

[5 minutes later]
SysDE1 → SDE1:
"Staging deployment complete. 
URL: https://staging.example.com
Smoke tests passing. Ready for QA."
```

### 4.2 Slack Group Chat Protocol

**When agents post in Slack groups:**
- Always prepend with agent name: `**AgentName:** message`
- Used for human notifications, NOT agent coordination
- Examples: standup updates, incident alerts, completion announcements

**When to post in Slack:**
- Daily standup (SDM posts summary of all agent status)
- Critical alerts (SysDE posts production incidents)
- Major milestones (SDM posts sprint completions)
- Blockers requiring human decision

**When NOT to post in Slack:**
- Routine agent-to-agent coordination → use direct messaging
- Intermediate progress updates → document in memory files
- Technical discussions between agents → direct messaging

### 4.3 Standup Protocol

**Daily standup (automated, scheduled):**
1. SDM sends direct message to each agent: "Standup time. Report: 1) What you did yesterday, 2) What you're doing today, 3) Blockers"
2. Each agent replies with status
3. SDM aggregates responses
4. SDM posts summary to Slack: `**SDM:** Daily Standup Summary - [date]`

**Format:**
```
**SDM:** Daily Standup Summary - Feb 13, 2026

SDE1:
- Yesterday: Implemented auth API (#42)
- Today: Writing tests for auth API
- Blockers: None

SDE2:
- Yesterday: Fixed bug #56 (login timeout)
- Today: Code review for SDE1's auth PR
- Blockers: None

SysDE1:
- Yesterday: Deployed v1.2.3 to staging
- Today: Setting up monitoring for auth endpoints
- Blockers: None

SysDE2:
- Yesterday: Investigated prod latency spike (resolved)
- Today: Implementing auto-scaling for API servers
- Blockers: Waiting on AWS quota increase (escalated to human)

Overall: Sprint on track. 1 blocker (AWS quota) requires human action.
```

### 4.4 Retrospective Protocol

**Weekly retrospective (scheduled, typically Friday):**
1. SDM sends direct message to all agents: "Retrospective time. Share: 1) What went well, 2) What could improve, 3) Action items"
2. Agents reply with reflections
3. SDM compiles insights
4. SDM posts to Slack for human review

**Purpose:**
- Continuous improvement
- Identify process bottlenecks
- Celebrate wins
- Adjust workflows

---

## 5. Memory & Context Management

### 5.1 Memory Architecture

**Per-Agent Memory:**
- Each agent has its own workspace directory
- Daily logs: `memory/YYYY-MM-DD.md`
- Long-term curated memory: `MEMORY.md`
- Role-specific docs (see each agent's Memory Requirements)

**Shared Memory:**
- `ROADMAP.md` - Strategic direction (owned by SDM, read by all)
- `SPRINT-CURRENT.md` - Active sprint (owned by SDM, updated by all)
- `POLICIES/` directory - Team policies (security, code standards, etc.)

### 5.2 Daily Log Pattern

**Every agent creates a daily log file:**

```markdown
# 2026-02-13 - [AgentName] Daily Log

## Morning
- [timestamp] Started work on task #42
- [timestamp] Question sent to SDM about auth approach
- [timestamp] SDM confirmed JWT approach

## Afternoon  
- [timestamp] Implemented JWT generation function
- [timestamp] Wrote 12 unit tests (all passing)
- [timestamp] Submitted PR #123 for review

## Evening
- [timestamp] Addressed code review feedback from SDE2
- [timestamp] PR approved and merged

## Blockers
- None today

## Tomorrow
- Write integration tests for auth API
- Deploy to staging with SysDE1
```

**Purpose:**
- Session continuity (agents wake up fresh each day)
- Audit trail of decisions
- Debugging aid when issues arise later
- Input for weekly retrospectives

### 5.3 MEMORY.md Pattern

**Long-term curated memory (not raw daily logs):**

```markdown
# Agent Memory - [AgentName]

## Core Principles
- Always ask for clarification before implementing ambiguous requirements
- Test-driven development: write tests first
- Document all architectural decisions in DECISIONS.md

## Lessons Learned
- 2026-02-10: JWT tokens need 1-hour expiry, not 24-hour (security requirement)
- 2026-02-11: Always run full test suite before requesting deployment
- 2026-02-12: Check staging environment before reporting "ready for QA"

## Preferences
- Preferred editor: VS Code
- Test framework: Jest for JavaScript, pytest for Python
- Git workflow: Feature branches, squash merges

## Frequent Patterns
- Auth implementation pattern: [link to example]
- API endpoint structure: [link to template]
- Error handling approach: [link to guide]
```

**Update Frequency:**
- Review daily logs weekly
- Extract lessons learned, repeated patterns
- Remove outdated information
- Keep to 2-3 pages maximum (curated, not comprehensive)

### 5.4 "Write It Down" Principle

**Critical rule: Mental notes don't persist. Files do.**

**If you want to remember something, write it to a file:**
- User says "remember this for later" → update relevant memory file
- You make a decision → add to DECISIONS.md
- You learn a lesson → update MEMORY.md
- You create a task → add to BACKLOG.md

**Anti-pattern:**
- "I'll remember to deploy this tomorrow" → NO, write to TODO.md
- "Mental note: this API has a rate limit" → NO, document in API_DOCS.md
- "I should refactor this later" → NO, add to TECH_DEBT.md

---

## 6. Skills & Tools Framework

### 6.1 Required Skills (All Agents)

**File Operations:**
- Read files (any location in workspace)
- Write files (create, update, append)
- Edit files (find/replace operations)
- List directories

**Git Operations:**
- Clone repositories
- Create branches
- Commit changes with descriptive messages
- Push to remote
- Pull latest changes
- View diff and status

**Shell Execution:**
- Run commands
- Capture output
- Handle errors
- Background long-running processes

**Slack Integration:**
- Post messages to channels
- Send direct messages to humans
- Format messages (markdown, code blocks)

### 6.2 Role-Specific Skills

**SDM Additional:**
- Task tracking system API (GitHub Projects, Jira, etc.)
- Markdown rendering (for roadmap docs)
- Slack threading (keep standup discussions organized)

**SDE Additional:**
- Programming language(s) specific to project
- Testing frameworks (unit, integration, e2e)
- Debugger tools
- Linting and code formatters
- Package managers (npm, pip, cargo, etc.)

**SysDE Additional:**
- CI/CD platform APIs (GitHub Actions, GitLab CI, etc.)
- Infrastructure CLIs (docker, kubectl, aws, gcloud, etc.)
- Monitoring APIs (Prometheus, Grafana, etc.)
- Log aggregation tools
- Security scanning tools

### 6.3 Skill Acquisition Pattern

**When an agent needs a new skill:**
1. Document the need in memory file
2. Research the tool/skill (read docs, examples)
3. Create test script to validate understanding
4. Use in production with error handling
5. Document usage pattern in MEMORY.md

**Example:**
```
SDE1 needs to use a new database library:
1. Add to memory: "Need to learn SQLAlchemy for task #45"
2. Read SQLAlchemy docs (focus on connection, queries)
3. Write test_database.py with basic CRUD operations
4. Use in feature implementation
5. Document common patterns in MEMORY.md under "Database Access"
```

---

## 7. Integration Requirements (Slack)

### 7.1 Slack Setup (Manual)

**Human must configure:**
- Slack workspace
- Bot app for each agent (5 total)
- OAuth tokens per bot
- Channel permissions
- Direct messaging enabled

**Each agent needs:**
- Unique bot name (e.g., "SDM-Bot", "SDE1-Bot", etc.)
- Bot user OAuth token
- Permission scopes: `chat:write`, `chat:write.public`, `im:write`

### 7.2 Message Format Standard

**All agent messages in Slack channels:**
```
**[AgentName]:** [message content]
```

**Examples:**
```
**SDM:** Daily standup summary: Sprint on track, 2 features complete.

**SDE1:** PR #123 ready for review - implemented auth API with tests.

**SysDE1:** 🚨 Production alert: API latency spike detected. Investigating now.
```

**Why:** Humans need to know which agent is speaking (can't rely on Slack username alone in multi-agent channels)

### 7.3 Notification Patterns

**When to notify humans:**

**SDM notifies:**
- Daily standup summaries
- Sprint completion
- Major milestones reached
- Blockers requiring human decision
- Weekly retrospective insights

**SDE notifies:**
- Feature complete and ready for review (if human QA required)
- Blocker requiring human input (e.g., unclear requirements)

**SysDE notifies:**
- Production incidents (critical)
- Deployment completions
- Infrastructure capacity warnings
- Security vulnerabilities detected

**Anti-pattern:**
- Don't spam humans with every small update
- Aggregate routine updates in daily standup
- Only interrupt for critical issues

### 7.4 Human Interaction Pattern

**When human replies in Slack:**
- Agent responsible for that area responds
- Other agents stay silent unless explicitly mentioned
- Agent updates relevant files with human's decision
- Agent confirms understanding before acting

**Example:**
```
**SysDE1:** Production deployment of v1.2.3 complete. All health checks passing.
Human (Product Owner): "Great! Can we add dark mode support in next sprint?"

**SDM:** Acknowledged. Adding "Dark Mode UI" to backlog. Will prioritize in sprint planning Monday. Estimated 3-5 days.