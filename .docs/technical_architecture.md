# Connect Cards API: Technical Architecture

## 1. Tech Stack Overview
- **Framework:** FastAPI (Python 3.x(Python 3.14.3 for the last update)) for high-performance async serving.
- **Database:** PostgreSQL accessed via SQLAlchemy ORM (Async Session `ext.asyncio`).
- **Migrations:** Alembic.
- **HTTP Client:** `httpx` (Asynchronous HTTP requests for webhook delivery).

## 2. Architectural Design Pattern
The application strictly enforces a **Repository-Service-Controller** layered architecture, heavily leveraging FastAPI's robust `Depends` injection system (`app/providers`).

1. **Controllers (`app/controllers`):** 
   - HTTP routing entry points.
   - Responsible for parameter parsing, validating Pydantic schemas, and managing pure HTTP constructs (e.g., retrieving the `BackgroundTasks` object).
2. **Services (`app/services`):**
   - The Business Logic layer.
   - Contains algorithmic routing (e.g., `CardService.scan_card()`, `IdentityService` rules).
   - Ignorant of raw HTTP mechanics (aside from explicitly raising `HTTPException`), delegating all persistent data manipulation to repositories.
3. **Repositories (`app/repositories`):**
   - The Data Access layer.
   - Abstracts raw SQL and SQLAlchemy `AsyncSession` commands into pythonic data access functions (e.g., `find_by_uid()`).

## 3. Core Technical Workflows

### 3.1 The High-Performance NFC Flow (`POST /scan`)
The scanning functionality is aggressively optimized because physical hardware readers require near-instant network responses.

1. **Initialization:** `CardController.scan_card` receives a `card_uid` and `project_id` from the reader and instantly triggers `CardService`.
2. **Audit Tracking:** The `CardService` instantly queues a `CARD_SCANNED` event to the `background_tasks`, preserving main-thread bandwidth.
3. **Optimized Querying:** Rather than querying Identity, Membership, and the Card sequentially, `card_repos.get_card_with_access_details` utilizes a composite SQL JOIN to fetch all related structures in a single atomic database trip, minimizing I/O latency.
4. **Validation:** In-memory business rules evaluate active status, Organization bindings, and Project validity.
5. **Authorization Dispatch:** The resulting `ACCESS_GRANTED` or `ACCESS_DENIED` logic is appended to the background task queue alongside the corresponding HTTP 200/403 return logic. 

### 3.2 Event Dispatcher & Webhook Engine
A zero-blocking dispatch loop handles notifications to third-party endpoints without degrading the main thread or starving the Database Connection Pool.

1. **Database Event Recording:** Inside `_log_event`, the event is seamlessly written to PostgreSQL via SQLAlchemy inside FastAPI's secondary `BackgroundTasks` loop.
2. **Routing Identification:** `EventDispatcher.dispatch_event` performs an asynchronous fetch through `WebhookRepository` to select un-paused webhook subscribers matching `event.event_type`.
3. **Detached ASGI Coroutines:** For every matching webhook, the service spawns `asyncio.create_task(WebhookService.send_webhook(...))`. This explicit detachment prevents slow `httpx` Webhook posts from hijacking FastAPI's SQL connection dependency (`get_db()` via `yield`), instantly returning the connection to the Postgres connection pool while the HTTP request resolves entirely in software memory.
4. **Network Resilience (Exponential Backoff):** Delivery is wrapped in `httpx.AsyncClient` blocks. It natively catches remote connection errors and uses zero-block `asyncio.sleep(delay)` loops for internal retries (`1s, 2s, 4s`) without killing overarching API workers.
5. **Security Mapping (HMAC):** Outgoing events append an `X-Signature` header locally computing `HMAC_SHA256(payload_body, custom_secret_key)`.

## 4. Entity Relationship Model
- **User / Identity:** Core identity construct.
- **Organization:** Top-level namespace containing Projects and Memberships.
- **Project:** Child of Organization, acts as a geographical/digital segment holding Readers.
- **Membership:** The intermediary linking an `Identity` to an `Organization` with specific role lists dictating access variables.
- **Card:** Contains state (`pending`/`active`), `uid`, and activation secrets. Bound sequentially to an `Identity` via `CardAssignmentHistory` blocks, enforcing immutable chronological security audits instead of destructive updates.
- **Reader:** Physical NFC reader device, mapped strictly to a targeted `project_id`.
- **Event:** A flat, fast-insert audit log mapping specific system occurrences (`CARD_SCANNED`, `CARD_REVOKED`, `ACCESS_GRANTED`) to standard relational IDs (`card_id`, `reader_id`, `project_id`) and flexible `JSONB`-style metadata.
- **Webhook:** External consumer payloads mapping target `URL` structures against specific `EventTypeEnum` hooks efficiently via the internal dispatcher.
