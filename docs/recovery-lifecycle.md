# Recovery lifecycle

`open -> approved -> recovered` is the normal review path. Reviewers may also choose `open -> rejected` or `approved -> rejected`. Invalid transitions return HTTP 409. Every accepted transition writes an audit event, reviewer label, note, and UTC timestamp. Retrying is a simulation: the source CSVs do not change.

The case table and audit history are the source of truth. A notification failure does not roll back a committed case.
