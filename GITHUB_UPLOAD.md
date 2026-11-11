# Publish on GitHub

Repository suggestion: `gamestick-ai-manager` (Public).

For preserving this project's nested directories, **use Git on your Mac instead of the web upload**:

```bash
cd /path/to/GameStick_AI_Manager
git init
git branch -M main
git add .
git commit -m "feat: initial GameStick AI Manager POC"
git remote add origin https://github.com/<your-github-username>/gamestick-ai-manager.git
git push -u origin main
```

Create an **empty public repository** on GitHub first; do not enable the GitHub-generated README, license or .gitignore because they are included here. GitHub authentication may prompt for browser or credential manager approval.

Alternatively use VS Code: File > Open Folder > select project folder, Source Control > Initialize Repository > Stage All > Commit > Publish Branch. This preserves project structure.

Never upload `workspace/`, `backups/`, `.env` or ROMs. These are excluded in `.gitignore`.
