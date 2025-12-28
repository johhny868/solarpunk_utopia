# Implementation Tasks: Standalone Android App

## Phase 1: Chaquopy Integration (Foundation)

### 1.1 Configure Chaquopy Gradle Plugin
- [ ] Add Chaquopy plugin to `frontend/android/build.gradle` (project level)
- [ ] Configure Chaquopy in `frontend/android/app/build.gradle` (app level)
- [ ] Set Python version to 3.11
- [ ] Configure pip packages from requirements.txt
- [ ] Handle native packages (cryptography, pynacl, bcrypt) with pre-built wheels

**Files to modify:**
- `frontend/android/build.gradle`
- `frontend/android/app/build.gradle`

### 1.2 Copy Python Backend to Android Assets
- [ ] Create script to copy `app/` directory to Android assets
- [ ] Create script to copy `valueflows_node/` to Android assets
- [ ] Create script to copy `mesh_network/` to Android assets
- [ ] Add copy task to Gradle build process
- [ ] Exclude unnecessary files (__pycache__, tests, etc.)

**Files to create:**
- `frontend/android/app/src/main/python/` (Python source location for Chaquopy)
- Gradle copy tasks

### 1.3 Modify Python Code for Android Compatibility
- [ ] Make database paths configurable via environment variables
- [ ] Replace psutil usage with Android-safe alternatives
- [ ] Make log paths configurable
- [ ] Ensure all file paths use Android app storage directory
- [ ] Remove/stub anthropic dependency (optional cloud feature)

**Files to modify:**
- `app/database/db.py` - configurable DB path
- `app/main.py` - configurable startup
- `valueflows_node/app/database.py` - configurable DB path
- Any files using psutil

---

## Phase 2: Android Service Layer (Kotlin)

### 2.1 Create Python Backend Service
- [ ] Create `SolarpunkBackendService.kt` as ForegroundService
- [ ] Initialize Chaquopy Python instance on service start
- [ ] Start DTN Bundle service (port 8000)
- [ ] Start ValueFlows service (port 8001)
- [ ] Handle service lifecycle (start, stop, restart)
- [ ] Create notification channel for foreground service

**Files to create:**
- `frontend/android/app/src/main/java/org/solarpunk/mesh/services/SolarpunkBackendService.kt`
- `frontend/android/app/src/main/java/org/solarpunk/mesh/services/PythonServerManager.kt`

### 2.2 Create Python Startup Script
- [ ] Create Python entry point that starts FastAPI with uvicorn
- [ ] Handle graceful shutdown
- [ ] Configure appropriate worker settings for mobile
- [ ] Add startup logging for debugging

**Files to create:**
- `frontend/android/app/src/main/python/android_main.py`

### 2.3 Integrate Service with App Lifecycle
- [ ] Start service when MainActivity launches
- [ ] Bind service to activity for status updates
- [ ] Handle service restart on app reopen
- [ ] Implement ServiceConnection for communication

**Files to modify:**
- `frontend/android/app/src/main/java/org/solarpunk/mesh/MainActivity.kt`

---

## Phase 3: WebView Integration

### 3.1 Configure Capacitor for Local Backend
- [ ] Update capacitor.config.ts to use localhost:8000
- [ ] Ensure cleartext HTTP is allowed
- [ ] Configure WebView to wait for backend startup
- [ ] Add loading screen while Python starts

**Files to modify:**
- `frontend/capacitor.config.ts`
- `frontend/src/App.tsx` (add loading state)

### 3.2 Create Backend Ready Bridge
- [ ] Create Capacitor plugin to check if Python is running
- [ ] Add health check polling in frontend
- [ ] Show "Starting services..." splash while backend initializes
- [ ] Handle backend startup failure gracefully

**Files to create:**
- `frontend/android/app/src/main/java/org/solarpunk/mesh/plugins/BackendBridgePlugin.kt`
- `frontend/src/plugins/BackendBridge.ts`

---

## Phase 4: Mesh Networking (Native Kotlin)

### 4.1 WiFi Direct Implementation
- [ ] Create `WifiDirectManager.kt` for P2P discovery
- [ ] Implement peer discovery with WifiP2pManager
- [ ] Handle connection negotiation
- [ ] Create socket-based data transfer for bundles
- [ ] Expose discovery/sync to Python via Chaquopy bridge

**Files to create:**
- `frontend/android/app/src/main/java/org/solarpunk/mesh/mesh/WifiDirectManager.kt`
- `frontend/android/app/src/main/java/org/solarpunk/mesh/mesh/PeerConnection.kt`

### 4.2 Bluetooth LE Discovery
- [ ] Create `BleManager.kt` for BLE scanning/advertising
- [ ] Implement GATT service for presence advertisement
- [ ] Handle background BLE with proper permissions
- [ ] Integrate with WiFi Direct (BLE discovers, WiFi Direct transfers)

**Files to create:**
- `frontend/android/app/src/main/java/org/solarpunk/mesh/mesh/BleManager.kt`

### 4.3 Python-Kotlin Mesh Bridge
- [ ] Create Kotlin class callable from Python (Chaquopy)
- [ ] Expose discoverPeers(), connectToPeer(), sendBundle()
- [ ] Handle async callbacks from Kotlin to Python
- [ ] Integrate with existing DTN sync logic

**Files to create:**
- `frontend/android/app/src/main/java/org/solarpunk/mesh/bridge/MeshBridge.kt`
- Python wrapper for calling Kotlin

---

## Phase 5: Panic Features (Native)

### 5.1 Duress PIN Implementation
- [ ] Create `PanicManager.kt` for panic feature coordination
- [ ] Implement alternate unlock detection
- [ ] Switch to decoy mode on duress PIN
- [ ] Notify Python backend of duress state

**Files to create:**
- `frontend/android/app/src/main/java/org/solarpunk/mesh/panic/PanicManager.kt`
- `frontend/android/app/src/main/java/org/solarpunk/mesh/panic/DecoyActivity.kt`

### 5.2 Quick Wipe Implementation
- [ ] Implement native database deletion (faster than Python)
- [ ] Delete all SQLite files in app storage
- [ ] Clear SharedPreferences
- [ ] Clear WebView cache and storage
- [ ] Kill Python process after wipe

**Files to modify:**
- `PanicManager.kt`

### 5.3 Dead Man's Switch
- [ ] Create WorkManager job for periodic check-in
- [ ] Implement auto-wipe after N days of no app open
- [ ] Store last-opened timestamp in encrypted SharedPreferences

**Files to create:**
- `frontend/android/app/src/main/java/org/solarpunk/mesh/panic/DeadManWorker.kt`

---

## Phase 6: Permissions & Polish

### 6.1 Android Permissions
- [ ] Add required permissions to AndroidManifest.xml:
  - INTERNET (localhost communication)
  - ACCESS_WIFI_STATE, CHANGE_WIFI_STATE
  - ACCESS_FINE_LOCATION (for WiFi Direct)
  - BLUETOOTH, BLUETOOTH_ADMIN, BLUETOOTH_SCAN, BLUETOOTH_ADVERTISE
  - FOREGROUND_SERVICE
  - RECEIVE_BOOT_COMPLETED (optional: start on boot)
- [ ] Implement runtime permission requests
- [ ] Handle permission denial gracefully

**Files to modify:**
- `frontend/android/app/src/main/AndroidManifest.xml`
- `MainActivity.kt`

### 6.2 App Startup Optimization
- [ ] Profile Python startup time
- [ ] Lazy load non-critical Python modules
- [ ] Optimize Chaquopy extraction (first run only)
- [ ] Add progress indicator during first-time setup

### 6.3 Battery Optimization
- [ ] Implement WorkManager for periodic sync (battery-friendly)
- [ ] Reduce WiFi Direct scan frequency when on battery saver
- [ ] Pause BLE advertising when screen off
- [ ] Add battery usage monitoring

---

## Phase 7: Testing & Release

### 7.1 Integration Testing
- [ ] Test Python backend starts successfully
- [ ] Test WebView connects to localhost backend
- [ ] Test all API endpoints work on device
- [ ] Test SQLite persistence across app restarts
- [ ] Test panic wipe functionality

### 7.2 Mesh Testing
- [ ] Test WiFi Direct discovery between two devices
- [ ] Test bundle sync over WiFi Direct
- [ ] Test BLE presence detection
- [ ] Test sync works in background

### 7.3 Build & Distribution
- [ ] Generate signed release APK
- [ ] Test on minimum spec device (Android 8, 2GB RAM)
- [ ] Document sideload installation process
- [ ] Create QR code for APK distribution

---

## File Structure After Implementation

```
frontend/android/app/src/main/
├── java/org/solarpunk/mesh/
│   ├── MainActivity.kt (modified)
│   ├── services/
│   │   ├── SolarpunkBackendService.kt
│   │   └── PythonServerManager.kt
│   ├── mesh/
│   │   ├── WifiDirectManager.kt
│   │   ├── BleManager.kt
│   │   └── PeerConnection.kt
│   ├── panic/
│   │   ├── PanicManager.kt
│   │   ├── DecoyActivity.kt
│   │   └── DeadManWorker.kt
│   ├── bridge/
│   │   └── MeshBridge.kt
│   └── plugins/
│       └── BackendBridgePlugin.kt
├── python/
│   ├── android_main.py
│   ├── app/                    (copied from project root)
│   ├── valueflows_node/        (copied from project root)
│   └── mesh_network/           (copied from project root)
└── AndroidManifest.xml (modified)
```

---

## Estimated APK Size Breakdown

| Component | Size |
|-----------|------|
| Python runtime (Chaquopy) | ~40MB |
| Python packages | ~30MB |
| Native libraries (crypto) | ~15MB |
| React frontend | ~5MB |
| Android runtime | ~10MB |
| **Total** | **~100MB** |

---

## Critical Path

1. **Phase 1.1-1.3**: Chaquopy setup (blocks everything)
2. **Phase 2.1-2.3**: Python service runs (blocks WebView)
3. **Phase 3.1-3.2**: App works offline (MVP!)
4. **Phase 4**: Mesh networking (true P2P)
5. **Phase 5**: Panic features (safety-critical)
6. **Phase 6-7**: Polish and release
