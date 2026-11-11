# ADR 0001: Reject unknown firmware profiles

**Decision:** write operations are supported only for the synthetic `demo-v1` profile.

**Context:** GameStick 4K firmware variants differ in the ROM directories, DB tables,
cover file naming and favorites handling. Assuming a fixed schema risks data loss.

**Consequences:** real cards can be inventoried manually as copies, but this POC
will not write to them. A real-device adapter is an explicit future milestone.
