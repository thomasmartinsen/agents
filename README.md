# Content agents

GitHub Copilot custom agents for Thomas Martinsen's work as a Global Tech
Evangelist at Twoday, Microsoft MVP, and agentic engineering community content
creator.

## Agents

| Agent | Use it for | Example prompt |
| --- | --- | --- |
| [Topic researcher](.github/agents/topic-researcher.agent.md) | Source-backed ideas, technology updates, and editorial briefs | "Find five timely agentic engineering topics for developers. Prioritize practical Microsoft ecosystem developments from the past two weeks." |
| [LinkedIn writer](.github/agents/linkedin-writer.agent.md) | Posts with a clear point of view and useful discussion prompts | "Turn this research brief into a LinkedIn post for engineering leaders. Use my personal voice, not an official Twoday announcement." |
| [Technical article writer](.github/agents/technical-article-writer.agent.md) | Tutorials, explainers, and experience reports | "Draft a developer tutorial from these notes. Cover prerequisites, evaluation, and failure modes. Mark any code you cannot verify." |
| [Video scriptwriter](.github/agents/video-scriptwriter.agent.md) | Short-form videos, explainers, and demo walkthroughs | "Create a three-minute video script explaining tool calling, with a visual plan and a realistic example." |
| [Content repurposer](.github/agents/content-repurposer.agent.md) | Channel-specific assets from existing material | "Turn this article into one LinkedIn post, a 60-second video script, and a five-slide carousel outline. Preserve its caveats." |

## Use

The profiles live in `.github/agents/*.agent.md`. Open this repository in a
Copilot client that supports custom agents, select an agent in the client's
agent picker, and provide your prompt and source material. Selection controls
vary by client; in Copilot CLI, use `/agent`.

A typical workflow is **Topic researcher -> a writing agent -> Content
repurposer**. Pass the research brief, source links, and relevant draft to the
next agent yourself; these profiles do not automatically invoke each other.
You can also use any agent independently.

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

## Tools and boundaries

Each profile enables only `read`, `search`, `edit`, and `web` tool aliases.
Available capabilities depend on the client: GitHub's cloud agent currently
does not map the `web` alias to browsing tools. Without web access, provide
source excerpts and links; the agents must identify claims they cannot verify
rather than imply live research was performed.

These agents draft content; they do not publish, schedule posts, contact people,
or access Microsoft 365, social accounts, or MVP reporting services. They do not
execute code, so generated code must be identified as untested unless actual
execution evidence is supplied. They return drafts in chat by default and edit
files only when asked, preserving unrelated work. Research output includes
sources; public-facing drafts keep attribution appropriate to the channel.

Profile format and tool aliases follow the
[GitHub custom agent configuration reference](https://docs.github.com/en/copilot/reference/custom-agents-configuration).