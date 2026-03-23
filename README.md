# peek-kit
AI-Powered App Analysis & Audit as a Claude Code MCP

peek-kit is an open-source MCP server + Claude Code skill that gives Claude the ability to autonomously explore any macOS application, analyze its user experience, map its full feature scope, and produce a rich human-readable audit report.

## Requirements
- macOS 13 Ventura or later
- Python 3.11 or later
- Claude Code

## Top Use Cases
Here are few examples of what you can accomplish using peek-kit:
- **Comprehensive UX Audits:** Automatically analyze every screen and interaction within an app to generate an actionable audit for learnability, visual hierarchy, and accessibility flaws.
- **Reverse-PRD Generation:** Run the tool against a competitor's app to extract its Epic structure, User Stories, and core "Secret Sauce" into a formatted Product Requirements Document.
- **Micro-Interaction Testing:** Instruct the agent to specifically focus on stress-testing complex signup flows or settings menus to uncover broken edge cases.

## Getting Started

### ⚡️ Quick Install — 30 seconds
Open Claude Code and paste this prompt. Claude will automatically install everything and configure the skill for you:

> **Install peek-kit:** run `claude mcp add -s user peek-kit -- uvx --from git+https://github.com/ufukkaraca/peek-kit.git peek-kit` and then run `curl -sL https://raw.githubusercontent.com/ufukkaraca/peek-kit/main/SKILL.md --create-dirs -o ~/.claude/skills/peek-kit/SKILL.md`. Finally, inform the user they must restart the `/claude` session to begin!

*(Note: on your first run, macOS will prompt you to grant Accessibility and Screen Recording permissions to your terminal).*

### 📦 Installing from PyPI (Coming Soon)
> [!NOTE]
> PyPI publishing is not yet available. Once live, the install will be even simpler:

> **Install peek-kit:** run `claude mcp add -s user peek-kit -- uvx peek-kit` and then run `curl -sL https://raw.githubusercontent.com/ufukkaraca/peek-kit/main/SKILL.md --create-dirs -o ~/.claude/skills/peek-kit/SKILL.md`. Finally, inform the user the `/peek-kit` skill is ready!

### 💻 Manual Installation (for Humans/Developers)
If you prefer to configure it yourself via the terminal, ensure you have [`uv`](https://docs.astral.sh/uv/getting-started/installation/) installed, then run:

1. **Configure the MCP server globally:**
```bash
claude mcp add -s user peek-kit -- uvx --from git+https://github.com/ufukkaraca/peek-kit.git peek-kit
```

2. **Install the Skill:**
```bash
curl -sL https://raw.githubusercontent.com/ufukkaraca/peek-kit/main/SKILL.md --create-dirs -o ~/.claude/skills/peek-kit/SKILL.md
```

Then simply start a new Claude Code session!

### 🛠 Local Development
For contributing or running from source:
```bash
git clone https://github.com/ufukkaraca/peek-kit.git
cd peek-kit
claude mcp add -s user peek-kit -- uv run --directory $(pwd) python -m peek_kit.server
cp SKILL.md ~/.claude/skills/peek-kit/SKILL.md
```

## Upgrading peek-kit
If you installed via the Quick Install method, simply re-run the install command to get the latest version from GitHub. After updating, restart your Claude Code session.

## Source Attributions & License
This project is open-source under the MIT License (see `LICENSE` file).

peek-kit stands on the shoulders of several incredible open-source libraries. We are deeply grateful to the maintainers of:
- [Model Context Protocol (MCP)](https://github.com/modelcontextprotocol): The foundational SDK enabling Claude to interface with this tool.
- [atomacos](https://github.com/vmdv/atomacos): The robust wrapper around macOS Accessibility APIs that makes UI enumeration and interaction possible.
- [pyobjc](https://github.com/ronaldoussoren/pyobjc): The essential bridge connecting Python to native macOS Cocoa and Quartz frameworks.
- [PyAutoGUI](https://github.com/asweigart/pyautogui): Enabling smooth mouse movement for visual click feedback.
- [Pillow](https://python-pillow.org/): Driving the image processing and annotation for our screenshots.
- [pydantic](https://docs.pydantic.dev/): Securing strict schema layouts for final JSON and Markdown reporting.
- [Jinja2](https://palletsprojects.com/p/jinja/): Powering the dynamic Markdown report templates.

## Privacy Notice
**IMPORTANT**: peek-kit captures screenshots and accessibility data of whatever is on screen.
- All data stays local — nothing is sent over the network by the MCP server.
- Reports and screenshots are written to the output directory and persist on disk.
- You should not run peek-kit while sensitive information (passwords, private documents) is visibly on screen.
