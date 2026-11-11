# Security and limits

- Only `demo-v1` card roots with an explicit `.gamestick-demo.json` marker can be written.
- The orchestrator has no write-capable LLM tools.
- `plan` is read-only. `apply` requires a verified full backup, `--execute`, and an exact phrase.
- `restore` also requires `--execute` and a different explicit phrase.
- Path traversal, symlink sources/destinations and unsupported extensions are rejected.
- At most 50 games per package, 512 MiB per ROM, 2 GiB total package data.
- Local update is not all-or-nothing: on interruption, run `restore` after review.
- The example ROM fixtures are not playable and contain no copyrighted game files.
- Do not run as root/admin for demo; filesystem access is local to your user.
- No automatic downloads of ROMs from third-party sites are provided.
- Device-specific `games.db` schemas, cover mapping, R2 favorites, and filesystem types
  require a dedicated audited adapter. A DB renamed to `games.db` is NOT enough.
