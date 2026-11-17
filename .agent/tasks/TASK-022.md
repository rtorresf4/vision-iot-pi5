# TASK-022 — M5.D MQTT EventPublisher Foundation

## STATUS
READY — task contract materialized; implementation requires ADS Human Gate approval and a clean task branch.

## MILESTONE
M5 — Event Distribution / M5.D — MQTT EventPublisher Foundation

## OBJECTIVE
Implement a minimal synchronous infrastructure MQTT publisher accepting an existing `InspectionEvent`, generating one UUIDv4 per logical publication, reusing `InspectionEventSerializer` unchanged, publishing its deterministic UTF-8 JSON bytes to the ratified topic with QoS 1, and returning only after verified broker PUBACK. Do not change domain outcomes or imply downstream consumer processing.

## ARCHITECTURE AUTHORIZATION
Architecture handoff dated 2026-11-17: *M5.D MQTT EventPublisher Boundary Ratification & TASK-022 Authorization*. Decisions: publisher boundary resolved; task materialization and implementation conditionally authorized following ADR-007 ratification. That prerequisite is satisfied by ADR-007 clarification integrated into `main` at `de2f172c898c6cab54dda41d42b010b088ec80d6`. M5 remains incomplete; M6 is not authorized.

Approved baseline:
- `paho-mqtt==2.2.0` only new production dependency.
- MQTT 3.1.1, `CallbackAPIVersion.VERSION2`, TCP, initial clean session, automatic reconnect disabled.
- QoS 1 and `retain=False`; topic `factory/line1/inspection/events`.
- Public lifecycle: `connect() -> None`, `publish(event: InspectionEvent) -> None`, `close() -> None`.
- Constructor-injected existing serializer and dedicated configured Paho client; publisher owns client connection/network loop/cleanup.
- Paho's **one internal network-processing thread** permitted by amended ADR-007. Application-facing publisher remains synchronous.
- CONNACK and PUBACK waits default to 5 seconds each, finite and positive. TCP establishment must also be bounded.
- `InspectionEventPublicationError` for transport failures, distinct from `InspectionEventSerializationError`.
- One event_id per logical publication; no application retries, automatic recovery, or persistence.

## MANDATORY REFERENCES AND PREFLIGHT
Read `GEMINI.md`, applicable `.agent/rules/`, `docs/architecture.md`, ADR-004, ADR-005, ADR-006, **amended ADR-007**, ADR-009, `docs/mqtt-inspection-event-contract.md`, `docs/project-context.md`, current domain and vision contracts, `src/vision_iot/infrastructure/inspection_event_serializer.py`, `src/vision_iot/infrastructure/__init__.py`, existing tests, and `pyproject.toml`.

Before changing files, verify local Git state and expected implementation branch, clean tree, task numbering, ratified ADR-007, Python runtime, dependency policy, and absence of an equivalent Architecture-v2 publisher. Do not treat legacy/prototype MQTT components as authoritative.

## SCOPE

### A. Dependency and client configuration
Modify `pyproject.toml` **only** to add `paho-mqtt==2.2.0` to production dependencies. Use a Paho client configured explicitly for MQTT 3.1.1, Callback API VERSION2, TCP, clean session, and disabled automatic reconnection. Broker host and port are explicit infrastructure parameters; never embed them in domain events. The injected client is dedicated to this publisher. If approved settings cannot be guaranteed or checked through the bounded design, escalate.

### B. Public publisher API
Create `src/vision_iot/infrastructure/mqtt_inspection_event_publisher.py`:
```python
class InspectionEventPublicationError(Exception):
    """MQTT connection or publication failure."""

class MqttInspectionEventPublisher:
    def connect(self) -> None: ...
    def publish(self, event: InspectionEvent) -> None: ...
    def close(self) -> None: ...
```
Constructor requires `InspectionEventSerializer` and a dedicated configured Paho client, plus only necessary host/port and finite positive timeout settings. CONNACK and PUBACK timeout defaults: **5 seconds** each. No abstract EventPublisher, result dataclass, factory, generic configuration or dependency-injection framework.

Extend `src/vision_iot/infrastructure/__init__.py` exports while retaining existing serializer exports.

### C. Connection lifecycle and synchronization
`connect()` establishes MQTT/TCP connection and starts the Paho-managed network loop. Report success only upon **accepted broker CONNACK**, never merely a successful call to client `connect()` or TCP handshake. Reject unsuccessful CONNACK and timeout explicitly. Synchronize callback notifications with the synchronous caller safely; avoid busy-waiting or unbounded waits. Disable automatic reconnect. Avoid application-level retry attempts.

**Critical:** the *TCP connection-establishment operation itself* must have a finite bound. A 5-second CONNACK wait does not bound an earlier blocking TCP connect. Verify real Paho 2.2.0 behavior; if no bounded solution fits the authorized scope, stop with `ARCHITECTURE_DECISION_REQUIRED` instead of claiming a guarantee.

`close()` explicitly disconnects and shuts down the library-owned loop; idempotence is acceptable. Ensure cleanup cannot conceal a preexisting publication failure.

### D. Publish and acknowledgment
`publish()` requires an accepted connection. Generate exactly one UUIDv4, invoke the existing serializer with `event_id`, and publish its exact bytes to `factory/line1/inspection/events` with `qos=1`, `retain=False`. Inspect immediate Paho result for rejection; wait for PUBACK using a bounded 5-second default. Check the completion state after waiting, e.g. `MQTTMessageInfo.wait_for_publish(timeout=...)` plus `is_published()`. Local acceptance alone is NOT success. Successful PUBACK means broker receipt, NOT consumer processing.

On timeout, delivery status is **uncertain**. Never reissue an application publish or generate another UUID automatically. Protocol-level retransmission by the same Paho publication may retain payload and event_id; no durable queue, generalized retry, automatic reconnect or cross-restart identity recovery.

### E. Errors and domain isolation
One infrastructure error `InspectionEventPublicationError` covers connection error/refusal, missing or rejected CONNACK, publication rejection, connection loss, missing PUBACK, timeout, and other bounded client publication failures. Preserve underlying client exceptions as causes when wrapping. Propagate existing `InspectionEventSerializationError` distinctly. Never mutate `InspectionEvent`, change inspection status/reason/evidence, or fabricate inspection results. No silent failure masking.

## EXACT ALLOWED CHANGES
Implementation Agent may create/modify **only**:
1. `src/vision_iot/infrastructure/mqtt_inspection_event_publisher.py` (new).
2. `src/vision_iot/infrastructure/__init__.py` (extend existing exports).
3. `tests/test_mqtt_inspection_event_publisher.py` (new).
4. `pyproject.toml` (add exactly approved runtime dependency).

If an additional module, dependency, config, test edit or ADR change appears necessary: stop and escalate, do not silently broaden the scope.

## FORBIDDEN CHANGES
No modifications to existing serializer, domain, vision, hardware, application or dashboard sources; existing tests; `docs/**`, `.agent/**`, `.github/**`, `apps/**`, `deploy/**`, `models/**`, `data/**`, `Makefile`, requirements or unrelated dependency metadata. Implementation Agent must not switch branches, commit, push, merge, rebase, or change Git configuration.

## REQUIRED DETERMINISTIC TESTS
Create broker-independent fake/mock Paho-client tests, with controlled callback synchronization (no actual network, broker, sleep, Pi, camera or ONNX model). Cover:
1. Exact topic, QoS 1, retain false.
2. Existing serializer reuse; exact payload mapping including generated UUIDv4.
3. Exactly one UUIDv4, one logical publish; no event mutation.
4. Accepted CONNACK required; rejected CONNACK, missing CONNACK timeout and local `connect()` return not being sufficient.
5. Verified bounded TCP-establishment behavior or explicit escalation if unimplementable.
6. Publishing before connection fails.
7. Local publish acceptance alone does not mean success.
8. Successful PUBACK completes; immediate publish rejection and missing PUBACK timeout fail explicitly.
9. Connection loss and client exceptions propagate via publication error with preserved cause.
10. No implicit repeat publish, no new event_id on timeout; ambiguous delivery reported accurately.
11. Serialization failures remain distinct, unmodified domain outcomes.
12. Network-loop start/stop and disconnect explicitly owned; cleanup does not mask errors.
13. No automatic reconnect, workers, durable queue or persistence.
14. Existing **101 regression tests** remain green.

Mocks must faithfully represent Paho callback and `MQTTMessageInfo` semantics, including `is_published()`; do not prove behavior solely by mocking the implementation's assumptions.

## ACCEPTANCE CRITERIA
- Exact approved dependency and protocol configuration; no unrelated packages.
- Public `connect/publish/close` API and constructor injection as approved.
- Accepted CONNACK gates publication and connection success.
- Finite TCP establishment and acknowledgment waits.
- Synchronous return only after confirmed QoS 1 PUBACK.
- Topic/QoS/retain exact; stable event_id per logical publication.
- Explicit error and ambiguous timeout semantics; serialization errors distinct.
- No domain or existing serializer changes; no application concurrency, automatic retries, persistence or broader framework.
- Broker-independent tests and regression tests pass; no real broker required for CI.
- Black, Ruff, mypy and pre-commit pass.
- Independent Review PASS, Human Gate approval, governed Git integration.

Green mocked tests alone do not prove real-broker interoperability.

## VALIDATION COMMANDS
From the root of the approved task branch:
```bash
git status -sb
PATH=.venv/bin:$PATH make lint
PATH=.venv/bin:$PATH make test
.venv/bin/pre-commit run --all-files
git diff --check
git diff --stat
git status --short
```
Inspect untracked new files directly; plain `git diff` does not cover them before staging. Do not bypass failures or silently adjust quality gates.

## STOP AND ESCALATE
Use `ARCHITECTURE_DECISION_REQUIRED` if Paho cannot distinguish PUBACK from local acceptance, TCP establishment cannot be bounded appropriately, automatic reconnection cannot be constrained, callback races make correctness unprovable, injected configuration cannot be validated, or broader thread/state/dependency scope is necessary. Use `TASK_BLOCKED` for missing prerequisites or dirty/unexpected branch state, `HUMAN_DECISION_REQUIRED` for governance decisions, `RETRY_EXHAUSTED` for unresolved bounded correction attempts. Never weaken the architecture silently.

## DELIVERABLES
Implementation Report: STATUS, FILES CHANGED, IMPLEMENTATION SUMMARY, TESTS ADDED, VALIDATION RESULTS (actual outputs), DEVIATIONS, BLOCKERS, OUT-OF-SCOPE OBSERVATIONS. Do not commit, merge or push. Stop at independent-review submission.
