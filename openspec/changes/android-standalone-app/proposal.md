# Proposal: Standalone Android App with Embedded Python Backend

**Status**: Draft
**Author**: Claude
**Created**: 2025-12-28

## Summary

Convert the Solarpunk Gift Economy Mesh Network into a fully standalone Android app that runs offline with no internet dependency. The app will embed the Python backend services using Chaquopy and keep the existing React frontend in a WebView via Capacitor.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    ANDROID APP (org.solarpunk.mesh)             │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              REACT FRONTEND (WebView)                    │    │
│  │   • Existing 34 pages, 32+ components                    │    │
│  │   • Zustand state, React Query                           │    │
│  │   • Connects to localhost:8000/8001/8002                 │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              ↓ HTTP                              │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              PYTHON BACKEND (Chaquopy)                   │    │
│  │   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │    │
│  │   │ DTN Bundle  │ │ ValueFlows  │ │   Bridge    │       │    │
│  │   │ Port 8000   │ │ Port 8001   │ │ Port 8002   │       │    │
│  │   └─────────────┘ └─────────────┘ └─────────────┘       │    │
│  │   • FastAPI + Uvicorn                                    │    │
│  │   • SQLite databases                                     │    │
│  │   • Ed25519/NaCl crypto                                  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              ↓                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              KOTLIN NATIVE BRIDGES                       │    │
│  │   • WiFi Direct P2P                                      │    │
│  │   • Bluetooth mesh                                       │    │
│  │   • Background service (ForegroundService)               │    │
│  │   • Panic gestures & secure wipe                         │    │
│  │   • Android permissions & lifecycle                      │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## Requirements

### SHALL (Mandatory)

1. **SHALL** run all backend services on-device without internet
2. **SHALL** start Python services automatically when app launches
3. **SHALL** persist SQLite databases in Android app storage
4. **SHALL** support WiFi Direct peer discovery and data sync
5. **SHALL** support Bluetooth LE for mesh proximity detection
6. **SHALL** implement panic features (quick wipe, duress PIN) natively
7. **SHALL** run background service for DTN sync when app is minimized
8. **SHALL** work on Android 8.0+ (API 26+) with 2GB RAM minimum

### SHOULD (Important)

9. **SHOULD** app size be under 150MB (target: 100MB)
10. **SHOULD** Python services start in under 5 seconds
11. **SHOULD** support QR code scanning for peer connection
12. **SHOULD** battery usage be reasonable for background mesh sync
13. **SHOULD** support sideload distribution (no Play Store)

### MAY (Optional)

14. **MAY** integrate with Android's Do Not Disturb for stealth mode
15. **MAY** support NFC for quick peer pairing
16. **MAY** allow optional connection to cloud relay for long-range sync

## Technical Decisions

### 1. Chaquopy Configuration

**Python Version**: 3.11 (best Chaquopy support)
**Bundled Packages**:
- fastapi, uvicorn, pydantic, pydantic-settings
- cryptography, pynacl (native builds required)
- aiosqlite
- bcrypt, mnemonic, structlog
- prometheus-client (optional, may skip for size)

**Excluded** (not needed on device):
- anthropic (AI agents connect to cloud only when available)
- psutil (use Android APIs instead)

### 2. Native Kotlin Components

Create a Kotlin module for Android-specific features:

```kotlin
// MeshNetworkBridge.kt
class MeshNetworkBridge {
    // WiFi Direct
    fun discoverPeers(): List<Peer>
    fun connectToPeer(peerId: String): Connection
    fun sendBundle(connection: Connection, bundle: ByteArray)

    // Bluetooth LE
    fun startBleAdvertising()
    fun scanForBleDevices(): List<Device>

    // Panic features
    fun triggerSecureWipe()
    fun isUnderDuress(): Boolean
}
```

### 3. Service Architecture

```kotlin
// SolarpunkBackendService.kt (ForegroundService)
class SolarpunkBackendService : Service() {
    private lateinit var pythonInstance: Python

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Start Python FastAPI servers
        pythonInstance = Python.getInstance()
        pythonInstance.getModule("app.main").callAttr("start_server", 8000)
        pythonInstance.getModule("valueflows_node.app.main").callAttr("start_server", 8001)

        return START_STICKY // Restart if killed
    }
}
```

### 4. Database Paths

Modify Python code to use Android-appropriate paths:

```python
# In app/database/db.py
import os
if os.environ.get('ANDROID_DATA'):
    DB_PATH = os.path.join(os.environ['ANDROID_DATA'], 'databases', 'dtn_bundles.db')
else:
    DB_PATH = 'data/dtn_bundles.db'
```

### 5. WebView Configuration

Update Capacitor to point to local Python server:

```typescript
// capacitor.config.ts
const config: CapacitorConfig = {
  server: {
    url: 'http://localhost:8000',  // Point to on-device Python
    cleartext: true,
  }
};
```

## Scenarios

### WHEN user opens app for first time THEN
1. Python backend starts (shows splash screen)
2. Database schema initializes
3. User sees onboarding flow
4. Key pair is generated and stored

### WHEN user is near another Solarpunk device THEN
1. WiFi Direct detects peer
2. DTN sync handshake occurs
3. Bundles are exchanged bidirectionally
4. UI updates to show new content

### WHEN user triggers panic wipe THEN
1. Native Kotlin immediately wipes SQLite databases
2. Python process is killed
3. Keys are destroyed
4. App shows decoy calculator interface

### WHEN app is in background THEN
1. ForegroundService keeps Python running
2. Periodic WiFi Direct scans for peers
3. BLE beacon advertises presence
4. Battery optimization allows background work

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Chaquopy increases APK size significantly | High | Optimize pip packages, exclude unused deps |
| cryptography/pynacl native build fails | High | Use pre-built Android wheels, fallback to pure Python |
| Python startup too slow | Medium | Lazy load modules, show splash screen |
| WiFi Direct requires user interaction | Medium | Use WiFi Aware (API 26+) for background |
| Battery drain from background sync | Medium | Intelligent scheduling, respect battery saver |

## Success Metrics

1. **APK size**: < 150MB (current web-only: 24MB)
2. **Startup time**: < 5 seconds to usable
3. **Peer discovery**: < 10 seconds in WiFi Direct range
4. **Bundle sync**: 100 bundles/minute over WiFi Direct
5. **Battery**: < 5% per hour in background sync mode

## Out of Scope

- iOS version (future work)
- Play Store distribution (sideload only)
- Cloud sync features (pure mesh)
- AI agents on-device (requires cloud when available)

## Dependencies

- Chaquopy Gradle plugin (com.chaquo.python)
- Android WiFi Direct API (WifiP2pManager)
- Android Bluetooth LE API (BluetoothLeScanner)
- Capacitor SQLite plugin (existing)
- Android ForegroundService

## References

- [Chaquopy Documentation](https://chaquo.com/chaquopy/doc/current/)
- [WiFi Direct Android Guide](https://developer.android.com/guide/topics/connectivity/wifip2p)
- [solarpunk_node_full_spec.md](../../solarpunk_node_full_spec.md) - Target mesh spec
- [ARCHITECTURE_CONSTRAINTS.md](../../ARCHITECTURE_CONSTRAINTS.md) - Design constraints
