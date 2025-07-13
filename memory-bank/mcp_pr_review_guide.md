# GitHub PR Review Process for MCP Development using Cline

## Step 1 – Gather PR Information

```bash
# Get PR details
gh pr view <PR-number> --json title,body,comments

# Get the full diff
gh pr diff <PR-number>

# Get files changed
gh pr view <PR-number> --json files

# Check PR status
gh pr checks <PR-number>
```

## Step 2 – Review the Code with Cline

```xml
<!-- Read specific files to understand changes -->
<read_file>
<path>path/to/modified/file.ts</path>
</read_file>

<!-- Search for specific patterns in the codebase -->
<search_files>
<path>src/</path>
<regex>pattern_to_search</regex>
<file_pattern>*.ts</file_pattern>
</search_files>
```

## Step 3 – Ask for a Decision

```xml
<ask_followup_question>
<question>Based on my review of PR #<PR-number>, I recommend [approving/requesting changes].
Here is my assessment:

- MCP protocol compliance (JSON-RPC 2.0)
- Resource management and cleanup
- Error handling with proper MCP error codes
- Test coverage and documentation
- Security and performance considerations
- Backward compatibility

Would you like me to proceed with this recommendation?</question>
<options>[
"Yes, approve the PR",
"Yes, request changes", 
"No, I'd like to discuss further"
]</options>
</ask_followup_question>
```

## Step 4 – Offer to Draft a Comment

```xml
<ask_followup_question>
<question>Would you like me to draft a comment for this PR that you can copy and paste?</question>
<options>[
"Yes, please draft a comment",
"No, I'll handle the comment myself"
]</options>
</ask_followup_question>
```

## Step 5 – Execute the Review Decision

### Approvals

```bash
# Single-line approval
gh pr review <PR-number> --approve --body \
"Thanks @username! This looks good – the MCP implementation follows the spec correctly."

# Multi-line approval
cat <<EOF | gh pr review <PR-number> --approve --body-file -
Thanks @username for this MCP implementation!

This looks solid – capability negotiation and error responses follow the MCP spec nicely.

The test coverage for the new resource types is comprehensive.

Great work!
EOF
```

### Change Requests

```bash
# Single-line change request
gh pr review <PR-number> --request-changes --body \
"Thanks @username! Please address the MCP protocol compliance issues mentioned."

# Multi-line change request
cat <<EOF | gh pr review <PR-number> --request-changes --body-file -
Thanks @username for working on this MCP feature!

The implementation looks promising, but a few concerns remain:

1. Error responses need MCP error codes (-32xxx).
2. Resource URI validation should be more robust.
3. Test coverage for connection-failure scenarios is missing.

Could you address these points? Happy to discuss if needed.
EOF
```

## MCP-Specific Review Checklist
- [ ] Protocol compliance (JSON-RPC 2.0) verified  
- [ ] Resource management and cleanup proper  
- [ ] Error handling with MCP error codes (-32xxx)  
- [ ] Capability negotiation logic correct  
- [ ] Security considerations addressed  
- [ ] Performance impact acceptable  
- [ ] Test coverage adequate  
- [ ] Documentation updated  
- [ ] Backward compatibility maintained  
- [ ] CI/CD pipeline passing  

## Quick Reference Commands

```bash
# List all open PRs
gh pr list

# Check out PR locally
gh pr checkout <PR-number>

# Add comment without approval/rejection
gh pr review <PR-number> --comment --body "Your comment here"

# View PR commits
gh pr view <PR-number> --json commits
```

## Example Review Flow
1. `gh pr view 3627 --json title,body,comments`  
2. `gh pr diff 3627`  
3. Inspect files with `<read_file>` and `<search_files>` tags  
4. Assess changes against MCP best practices  
5. Prompt user for approval or change request  
6. Draft comment if requested  
7. Execute review with the appropriate `gh pr review` command
