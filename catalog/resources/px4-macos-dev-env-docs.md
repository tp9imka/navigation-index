# macOS Development Environment (PX4 Guide)

`res:px4-macos-dev-env-docs` - doc - <https://docs.px4.io/main/en/dev_setup/dev_env_mac.html>

**By:** PX4 Dev Team - **Year:** 2026 - **Level:** intro - **Access:** open

Native macOS setup for PX4 SITL with Gazebo Harmonic via Tools/setup/macos.sh --sim-tools, which pulls gz from a locked conda-forge env through pixi.

## Key takeaways

- Works on Apple Silicon; CI runs on Apple Silicon only
- Raise ulimit to 2048 or the link step fails
- Installs XQuartz and trusts third-party Homebrew taps

**Concepts:** [Simulation and HIL/SITL](../../catalog/concepts/simulation.md), [Autopilots and flight control](../../catalog/concepts/autopilot.md)

**Tags:** `px4`, `macos`, `apple-silicon`, `sitl`

## Related

- explains: [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md)

_Indexed by lane(s): close-area-sims_
