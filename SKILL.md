# peek-kit Analysis Skill

**PREREQUISITE CHECK:** Before doing anything, check your available tools. If `get_peek_kit_version` is NOT available, immediately inform the user that the MCP server is missing. Offer to automatically install it for them by running `claude mcp add -s user peek-kit -- uvx --from git+https://github.com/ufukkaraca/peek-kit.git peek-kit` in their terminal, and remind them they must restart the Claude session to connect. Do NOT attempt the audit until the tools are active.

## Trigger & Mode Entry
Activate this skill when user says: 'Analyze [App]', 'Peek [App]', 'Audit [App]', '/peek-kit', or asks you to reverse-engineer an app.
**CRITICAL INTERACTIVE FLOW:**
When this skill is triggered, you MUST execute the following sequence BEFORE any audits:
1. **Version Check:** Call the `get_peek_kit_version` tool. Note the version internally.
2. **Permissions Check:** Call the `check_system_permissions` tool. If either `accessibility` or `screen_recording` is `false`, you MUST immediately stop, tell the user which permissions are missing, and ask them to grant them before trying again.
3. **Ask Questions:** If permissions are granted, tell the user the current Peek-Kit version and ask them these three questions in a numbered list:
   - **Target:** What application would you like me to audit?
   - **Scope:** Should I perform a full, comprehensive audit, or focus on a specific area (e.g., settings menus)?
   - **Context (Optional):** Do you have any documentation or user research you can share?

**Wait for the user to answer.** Once they reply, formulate a short plan in the chat and begin execution!

## Exploration Strategy
1. Start with `get_current_state` to establish the baseline and detect constraints (like auth walls or missing accessibility items).
2. If an auth wall is detected, call `request_human_action` before any other exploration.
3. Enumerate top-level navigation using `get_menu_structure`.
4. Map primary user flows first: onboarding, core action, settings, account.
5. Probe secondary flows: error states, empty states, modals.
6. Target a minimum of 15 distinct screens for a complete audit. Keep track of explored paths. Avoid infinite loops. Stop exploring a branch after 3 levels of depth with no new UI patterns.
7. For custom GUIs (like Electron apps e.g., Notion, Linear), you might get a warning about `vision_mode`. Rely heavily on screenshots and coordinate-based clicking if standard element clicking fails. 

## Human-Handoff Protocol
- Auth wall signals: login, signup, paywall, CAPTCHA, 2FA prompt, SSO redirect.
- Immediately call `request_human_action()` when these occur. Do NOT type passwords or bypass automatically!
- After the user resumes, call `check_auth_state()` to verify the gate cleared.
- Include user tier in report coverage section.
- If skipped, document inaccessible areas.

## Analysis Dimensions
Evaluate the UX quality rubric (1-5):
- Learnability
- Efficiency
- Error prevention
- Feedback
- Consistency
- Accessibility
- Visual hierarchy
- Error recovery

Product Intelligence Dimensions:
- Feature inventory
- Secret sauce
- Design philosophy
- Onboarding strategy
- Monetization touchpoints 
- Trust signals
- Rough edges

## Report Structure
Draft findings against the exact structure outlined by `AuditReport` schema and write it down.
Make sure you call `write_audit_report` when finished. Use screenshots via `save_screenshot_artifact`.

## Reverse-PRD Mode
If a `reverse-PRD` is requested, call `write_reverse_prd`. Make opinionated choices. Construct meaningful Epics and User stories that an engineer can build.

## Safety & Failure Rules
- **No Hallucinations:** If a tool like `get_accessibility_tree` or `take_screenshot` fails or returns an error, DO NOT invent UI elements and DO NOT generate fake reports. Stop the audit immediately and notify the user about the failure.
- Never type in password fields (`AXSecureTextField`).
- Never submit forms that trigger transactions or send messages.
- Never click Delete, Remove, Uninstall.
- If uncertain whether an action is safe, skip it.
