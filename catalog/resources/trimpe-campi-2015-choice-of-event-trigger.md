# On the Choice of the Event Trigger in Event-based Estimation

`res:trimpe-campi-2015-choice-of-event-trigger` - paper - <https://marco-campi.unibs.it/pdf-pszip/EBCCSP-2016.pdf>

**By:** Sebastian Trimpe, Marco C. Campi - **Year:** 2015 - **Level:** advanced - **Access:** open

EBCCSP 2015 paper (doi 10.1109/EBCCSP.2015.7300691). Compares send-on-delta, measurement-based, variance-based and relevant-sampling triggers for a scalar Kalman filter and derives two new ones. Shows that a trigger which does not need the measurement value (variance-based) can be precomputed offline as a time-based schedule. Full text read from extracted PDF text; conclusion section not located.

## Key takeaways

- Variance-based triggering thresholds the prediction variance c^2 P(k|k-1) + r and ignores the measurement value
- Optimal variance-based decisions can be precomputed offline from the model and run as a fixed schedule
- So a covariance-threshold fix trigger with sure arrival is a fixed schedule in disguise; scheduling only gains from success probability or delay

**Concepts:** [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `event-triggered-estimation`, `variance-based-triggering`, `kalman-filter`, `sensor-scheduling`

## Referenced by

- [Predictive and Self Triggering for Event-based State Estimation](../../catalog/resources/trimpe-2016-predictive-self-triggering-estimation.md) (same_author)

_Indexed by lane(s): innovation-pa-scheduling_
