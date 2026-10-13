# LifeLink AI — Architecture and Demo Data Flow

This diagram documents the existing intended architecture at the project level. It does not imply that every external integration (Firebase, maps, GPS, or live deployment) is configured in every environment.

## High-level architecture

```mermaid
flowchart TB
    subgraph Client["Single Flutter application"]
      UI["Role-aware UI / Material 3"]
      AUTH["JWT session + route guards"]
      RT["Authenticated WebSocket client"]
      UI --> AUTH
      UI <--> RT
    end

    subgraph API["FastAPI backend"]
      ROUTER["Versioned API routers (/api/v1)"]
      AUTHZ["Authentication + role/object authorization"]
      DOMAIN["Emergency / Dispatch / Responder / Hospital / Police / Family / Admin services"]
      NOTIFY["Notification persistence + optional FCM"]
      ROUTER --> AUTHZ --> DOMAIN
      DOMAIN --> NOTIFY
    end

    DB[("PostgreSQL")]
    CACHE[("Redis / realtime support where configured")]
    FCM["Firebase Cloud Messaging (optional)"]

    AUTH -->|"HTTPS REST in deployment"| ROUTER
    RT <-->|"Authenticated events"| CACHE
    DOMAIN <--> DB
    NOTIFY --> DB
    NOTIFY -. "only when configured" .-> FCM
    FCM -. "device notification" .-> UI
```

## Emergency demo sequence

```mermaid
sequenceDiagram
    participant C as Citizen (Flutter)
    participant API as FastAPI
    participant DB as PostgreSQL
    participant P as Police (same app, role-aware)
    participant R as Responder (same app, role-aware)
    participant H as Hospital dashboard
    C->>API: Authenticate and submit confirmed test SOS
    API->>DB: Persist emergency and timeline
    API-->>C: Emergency ID and current status
    P->>API: View queue and request dispatch
    API->>DB: Validate permissions and persist dispatch/assignment
    API-->>R: Assignment via API/realtime when configured
    API-->>H: Incoming emergency/resource event when configured
    R->>API: Update assignment status
    API->>DB: Persist lifecycle and resource changes
    API-->>C: Updated status/timeline
```

## Trust boundaries and data ownership

- The Flutter app is one client with separate role-aware routes; roles are not separate applications.
- FastAPI is the authority for authentication, authorization, emergency state, dispatch state, and hospital-resource updates.
- PostgreSQL stores persistent domain state. The client must not treat a local UI state or WebSocket event as the authoritative record.
- Realtime events improve responsiveness; clients should reload/synchronize from the API after reconnecting.
- Notifications are persisted by the backend. FCM is optional and must be separately configured and tested.
- Location permission is explicit. Do not request background location for the current foreground SOS flow.
- Use synthetic demo accounts and test coordinates. Never put secrets or real emergency/patient data into the repository.

## API and local endpoints

- Local FastAPI documentation: `http://127.0.0.1:8000/docs`
- Local API prefix: `/api/v1`
- Flutter web local API base: `http://127.0.0.1:8000/api/v1` (CORS must allow the chosen local web origin).
- Android emulator API base: `http://10.0.2.2:8000/api/v1`.

See the root README and `Doc/DAY7_DEMO_RELEASE_CHECKLIST.md` for setup and release evidence requirements.
