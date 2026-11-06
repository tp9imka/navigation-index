# Как я научил квадрокоптер возвращаться домой без GPS: алгоритм «верёвочной лестницы»

`res:habr-rope-ladder-return-home-2025` - blog - <https://habr.com/ru/articles/932254/>

**By:** Habr author (name not verified; companion repo by VohminV) - **Year:** 2025 - **Level:** intro - **Access:** open

English: 'How I taught a quadcopter to return home without GPS: the rope-ladder algorithm'. Explains why integrating optical flow velocity drifts so that the drone ends up offset after return, and replaces it with stored keyframe 'rungs' matched on the way back. Habr blocked automated fetch, so author and date are not verified (year inferred from the companion repo, created July 2025); content summarised from search snippets and the repo README.

## Key takeaways

- Flow integration error accumulates; keyframe matching bounds it for return-home
- Teach-and-repeat is a pragmatic answer when only the way back matters

## Deep dives

- [ua-ru-sources-overview](../../docs/landscape/ua-ru-sources-overview.md) (landscape)

**Concepts:** [Visual(-inertial) odometry](../concepts/vio.md), [Place recognition and loop closure](../concepts/place-recognition.md)

**Tags:** `lang:ru`, `habr`, `optical-flow`, `return-to-home`

## Related

- has_code: [rope-ladder-tracker](../repos/vohminv__rope-ladder-tracker.md)

_Indexed by lane(s): ua-ru-sources_
