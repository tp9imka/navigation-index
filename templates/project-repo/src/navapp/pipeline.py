"""Wires PoseSource => NavFilter => IntegrityMonitor => Publishers. Detect before fuse."""
from __future__ import annotations

from typing import Iterable, Optional

from .interfaces import Health, IntegrityMonitor, NavFilter, PoseSource, Publisher
from .publishers import JsonlPublisher


def run(source: PoseSource, nav: NavFilter, monitor: IntegrityMonitor,
        publishers: Iterable[Publisher] = (), log: Optional[JsonlPublisher] = None) -> list[dict]:
    publishers = list(publishers)
    records = []
    for epoch in source.epochs():
        nav.predict(epoch)
        verdict = monitor.check(epoch, nav.innovation(epoch))
        if verdict.health == Health.TRUSTED:
            nav.update(epoch)
        state = nav.state(epoch.t)
        for pub in publishers:
            pub.publish(state, verdict)
        if log:
            records.append(log.publish(state, verdict, truth=epoch.truth,
                                       fix_present=epoch.absolute is not None))
    return records
