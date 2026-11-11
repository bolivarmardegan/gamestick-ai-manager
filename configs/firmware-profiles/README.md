# Firmware adapter boundary

The included `demo-v1` SQLite schema is **not** the actual schema of an M8/M15/GameStick 4K device.
Your physical SD card may contain a SQLite DB such as `games.db`, with tables such as
`tbl_game`, but table structures and image mappings depend on firmware. No generic
write adapter is safe. The POC rejects all unrecognized devices.

Future real adapter development requires: read-only inventory; firmware fingerprint;
verified copy of the DB and metadata; tests against sanitized fixture; mapping of
ROM path/title/image/favorite fields; lab device validation; explicit opt-in.

`database.sqlite3` and favorites / R2 controls should be regarded as device-specific.
