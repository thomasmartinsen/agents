# Custom agents

GitHub Copilot custom agents for Thomas Martinsen's work as a Global Tech
Evangelist at Twoday, Microsoft MVP, and agentic engineering community content
creator, alongside personal strategy, capacity, relationships, and wellbeing.

## Agents

| Agent | Use it for | Example prompt |
| --- | --- | --- |
| [AI daily post](.github/agents/ai-daily-post.agent.md) | Short, verified internal AI news with a separate personal perspective | "Draft today's AI news post from this announcement, with sources and a perspective for my review." |
| [Topic researcher](.github/agents/topic-researcher.agent.md) | Source-backed ideas, technology updates, and editorial briefs | "Find five timely agentic engineering topics for developers. Prioritize practical Microsoft ecosystem developments from the past two weeks." |
| [LinkedIn writer](.github/agents/linkedin-writer.agent.md) | Posts with a clear point of view and useful discussion prompts | "Turn this research brief into a LinkedIn post for engineering leaders. Use my personal voice, not an official Twoday announcement." |
| [Technical article writer](.github/agents/technical-article-writer.agent.md) | Tutorials, explainers, and experience reports | "Draft a developer tutorial from these notes. Cover prerequisites, evaluation, and failure modes. Mark any code you cannot verify." |
| [Video scriptwriter](.github/agents/video-scriptwriter.agent.md) | Short-form videos, explainers, and demo walkthroughs | "Create a three-minute video script explaining tool calling, with a visual plan and a realistic example." |
| [Content repurposer](.github/agents/content-repurposer.agent.md) | Channel-specific assets from existing material | "Turn this article into one LinkedIn post, a 60-second video script, and a five-slide carousel outline. Preserve its caveats." |
| [Chief of Staff](.github/agents/chief-of-staff.agent.md) | Capacity, commitments, calendar trade-offs, and protected time | "Review this week's commitments and suggest what to defer to protect thinking and recovery time." |
| [Health Guardian](.github/agents/health-guardian.agent.md) | Non-clinical workload, recovery, and wellbeing reviews | "Review this travel plan for recovery risks and suggest practical adjustments." |
| [Innovation Scout](.github/agents/innovation-scout.agent.md) | Emerging signals, future scenarios, and bounded experiments | "Find three evidence-backed signals in agentic engineering and propose small experiments." |
| [Opportunity Filter](.github/agents/opportunity-filter.agent.md) | Invitations and projects assessed against value and displaced commitments | "Assess this speaking invitation against my current commitments, including preparation and travel." |
| [Relationship Manager](.github/agents/relationship-manager.agent.md) | Thoughtful follow-ups, reconnections, and consent-aware introductions | "Use these meeting notes to suggest three meaningful follow-ups and draft messages." |
| [Strategic Advisor](.github/agents/strategic-advisor.agent.md) | Strategic options, assumption testing, and long-term decisions | "Challenge this initiative, compare the alternatives, and propose a low-cost experiment." |

## Install from the marketplace

Each of the 12 agents is also an independently installable Copilot CLI plugin
under `plugins/<agent-id>/`. Register the
[marketplace](https://github.com/thomasmartinsen/marketplace), then install the
agents you need:

```sh
copilot plugin marketplace add thomasmartinsen/marketplace
copilot plugin marketplace browse thomasmartinsen
copilot plugin install linkedin-writer@thomasmartinsen
copilot plugin install chief-of-staff@thomasmartinsen
```

Use any filename from the table above without `.agent.md` as the plugin ID.
After installation, start a new session and select the agent with `/agent`.
You do not need to open this repository to use an installed plugin. Both
repositories are private; installation requires GitHub access to both.

To update an installed agent:

```sh
copilot plugin marketplace update thomasmartinsen
copilot plugin update linkedin-writer
```

Plugins preserve the original profiles, including their tool restrictions,
personal context, and safety boundaries. They do not add tools, MCP servers,
account access, or background automation. Existing project or personal agents
with the same ID take precedence over plugin-provided agents.

## Use from this repository

The profiles live in `.github/agents/*.agent.md`. Open this repository in a
Copilot client that supports custom agents, select an agent in the client's
agent picker, and provide your prompt and source material. Selection controls
vary by client; in Copilot CLI, use `/agent`.

A typical workflow is **Topic researcher -> a writing agent -> Content
repurposer**. Pass the research brief, source links, and relevant draft to the
next agent yourself; these profiles do not automatically invoke each other.
You can also use any agent independently.

For advisory work, a useful sequence is **Innovation Scout -> Opportunity
Filter -> Chief of Staff**, with Strategic Advisor, Health Guardian, or
Relationship Manager input as needed. Pass only relevant, authorized context
between agents. Reviews run when invoked, not continuously in the background.

For better results, include:

- The intended audience, channel, goal, and language.
- Notes, source links, code, or a transcript the agent may use.
- A sample of your writing and any length or format constraints.
- Whether you are speaking personally or preparing an approved Twoday message.

The agents use the language of your request unless you specify another language.
They default to a practical, approachable personal voice, not an assumed Twoday
brand guide or an official Microsoft position. Actual experiences, customer
stories, company messaging, and personal opinions must come from you or approved
source material.

## Codex plugins

The same marketplace also supports Codex:

```sh
codex plugin marketplace add thomasmartinsen/marketplace
codex plugin list --marketplace thomasmartinsen --available --json
codex plugin add linkedin-writer@thomasmartinsen
```

Start a new Codex session and ask it to use the installed plugin's skill.
Codex plugins expose these roles as **skills**, not native custom subagents.
Their instructions include the same written tool boundaries as the Codex
profiles below; these are guidance, not per-tool permission enforcement.

Each package includes a `.codex-plugin/plugin.json` referencing `codex-skills/`.
This separate skill directory prevents Copilot from also discovering the Codex
skill as a second copy of its agent. The Codex marketplace catalog lives at
`.agents/plugins/marketplace.json` in the marketplace repository; Copilot uses
`.github/plugin/marketplace.json`. Their Git source formats differ, so copying
the Copilot catalog into Codex's manifest location is not sufficient.

If registration previously failed with "marketplace root does not contain a
supported manifest", retry the add command. To refresh an existing registration,
use `codex plugin marketplace upgrade thomasmartinsen`.

## Codex custom agents

The same agents are available to Codex as project-scoped custom agents in
`.codex/agents/*.toml`, using the
[Codex custom agent format](https://developers.openai.com/codex/subagents)
(`name`, `description`, `developer_instructions`). Agent names use snake_case,
for example `linkedin_writer`. Ask Codex to use one, such as "Have
linkedin_writer draft a post from this brief."

`.github/agents/*.agent.md` is the source of truth. After changing a profile,
regenerate the Codex files:

```sh
python3 scripts/sync_codex_agents.py            # update .codex/agents
python3 scripts/sync_codex_agents.py --install  # also copy to ~/.codex/agents for all projects
python3 scripts/sync_codex_agents.py --check    # fail if out of date
```

Codex custom agents cannot restrict individual tools, so each profile's `tools`
list is converted into written tool boundaries in its instructions. Codex agents
inherit the parent session's sandbox and approval settings.

## Maintaining plugins

`.github/agents/*.agent.md` remains the source of truth for both generated
formats. Do not edit files under `plugins/` or `.codex/agents/` directly.
After editing a profile, regenerate both and check the results:

```sh
python scripts/sync_codex_agents.py
python scripts/sync_plugins.py
python scripts/sync_codex_agents.py --check
python scripts/sync_plugins.py --check
python -m unittest discover -s scripts -p "test_*.py"
```

The plugins use the supported Copilot-specific manifest format: each root
`plugin.json` declares its `agents/` directory. The packaged agent is an
unchanged copy of its source profile. CI checks both generated formats and
runs the packaging tests.

When adding or removing agents, changing descriptions, or releasing a new
version, export the catalog into a separate checkout of the marketplace:

```powershell
python scripts\sync_plugins.py --marketplace-output C:\repos\marketplace\.github\plugin\marketplace.json
python scripts\sync_plugins.py --codex-marketplace-output C:\repos\marketplace\.agents\plugins\marketplace.json
python scripts\sync_plugins.py --check --marketplace-output C:\repos\marketplace\.github\plugin\marketplace.json
python scripts\sync_plugins.py --check --codex-marketplace-output C:\repos\marketplace\.agents\plugins\marketplace.json
```

These commands replace the entire target catalogs, which currently list only these
agents. If the marketplace later includes other plugins, merge the exported
entries rather than overwriting them. The catalog references `main` in this
repository, so merge plugin changes here before the corresponding marketplace
update. For a release, update `VERSION` in `scripts/sync_plugins.py`, regenerate,
and commit the packages and catalog in their respective repositories. Existing
installations update explicitly; the catalog does not pin immutable releases.

## Tools and boundaries

Profiles use a role-specific subset of `read`, `search`, `edit`, and `web` tool
aliases. The six advisory profiles are read-only; only Innovation Scout and
Strategic Advisor among them enable web research.
Available capabilities depend on the client: GitHub's cloud agent currently
does not map the `web` alias to browsing tools. Without web access, provide
source excerpts and links; the agents must identify claims they cannot verify
rather than imply live research was performed.

These agents draft content and recommendations; they do not publish, schedule posts, contact people,
or access Microsoft 365, social accounts, or MVP reporting services. They do not
execute code, so generated code must be identified as untested unless actual
execution evidence is supplied. They return drafts in chat by default and edit
files only when asked, preserving unrelated work. Research output includes
sources; public-facing drafts keep attribution appropriate to the channel.

Health Guardian provides non-clinical support, not diagnosis or treatment.
Personal context may be outdated and should be confirmed before relying on it.
Some profiles contain sensitive personal and family information; review this
before sharing the repository or making it public. Tool aliases do not grant
access to private calendars, accounts, or medical records.

Profile format and tool aliases follow the
[GitHub custom agent configuration reference](https://docs.github.com/en/copilot/reference/custom-agents-configuration).