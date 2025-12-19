# Android Deployment Progress

**Status:** Partially Implemented - Needs Java 11+ to build APK
**Date:** 2025-12-19

## What Was Accomplished

### ✅ Capacitor Setup (Completed)
- Installed Capacitor and Android platform
- Created `capacitor.config.ts` with proper configuration
- Set minimum Android SDK to 26 (Android 8.0) per architecture constraints
- Added Android project structure in `frontend/android/`

### ✅ Android Manifest Configuration (Completed)
- Added all required permissions for mesh networking:
  - WiFi Direct permissions (ACCESS_WIFI_STATE, CHANGE_WIFI_STATE)
  - Location permissions (required for WiFi Direct on Android)
  - Bluetooth permissions (for fallback mesh)
  - NEARBY_WIFI_DEVICES for Android 13+
  - Foreground service permissions for background sync
- Configured hardware feature declarations

### ✅ WiFi Direct Mesh Plugin (Completed - Native Android Code)
- Created Capacitor plugin interface at `frontend/src/plugins/mesh-network.ts`
- Implemented native Android plugin at `frontend/android/app/src/main/java/org/solarpunk/mesh/MeshNetworkPlugin.java`
- Features implemented:
  - WiFi Direct peer discovery
  - Connect/disconnect to peers
  - Peer list management
  - Broadcast receiver for WiFi P2P events (`WiFiDirectBroadcastReceiver.java`)
  - Permission handling for Android 8+ and 13+
- Created web fallback implementation for development

### ✅ Frontend Build System (Completed)
- Frontend builds successfully with `npx vite build`
- Web assets sync to Android project with `npx cap sync android`
- Capacitor detects SQLite plugin correctly

### ⚠️ Local Storage Layer (Started - TypeScript Errors)
Created but not integrated due to type mismatches:
- `frontend/src/storage/sqlite.ts` - SQLite wrapper with full schema
- `frontend/src/storage/local-api.ts` - Local-first API implementation
- `frontend/src/api/adaptive-valueflows.ts` - Adaptive API switcher

**Issues:**
- Type definitions don't match between local-api and actual ValueFlows types
- Need to align with actual `Listing` type structure (agent_id, resource_spec_id, etc.)
- Files removed temporarily to allow build to proceed

## What Remains

### 🔴 Critical Blockers

####  1. Install Java 11+ (REQUIRED TO BUILD APK)
Current system has Java 8, but Android Gradle plugin requires Java 11+.

**Options:**
```bash
# Option A: Install via Homebrew
brew install openjdk@17
sudo ln -sfn /opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk /Library/Java/JavaVirtualMachines/openjdk-17.jdk

# Option B: Download from Oracle/Azul
# https://www.oracle.com/java/technologies/downloads/
# or https://www.azul.com/downloads/?package=jdk

# Then set JAVA_HOME
export JAVA_HOME=$(/usr/libexec/java_home -v 17)
```

#### 2. Build APK
Once Java 11+ is installed:
```bash
cd frontend/android
./gradlew assembleDebug

# APK will be at:
# android/app/build/outputs/apk/debug/app-debug.apk
```

#### 3. Fix Local Storage TypeScript Errors
The local-first data layer needs to match the actual ValueFlows type definitions:
- Use `listing_type`, `agent_id`, `resource_spec_id` (not `action`, `providerId`, etc.)
- Match `EconomicEvent` structure (provider_id not providerId)
- Use correct `Exchange` fields
- Fix all type mismatches in `local-api.ts`

#### 4. Implement Data Sync
- DTN bundle creation from sync queue
- Bundle transmission over WiFi Direct sockets
- Bundle reception and unpacking
- Conflict resolution for offline edits

#### 5. Create Sideload Distribution
- QR code generator for APK download
- Mesh-based APK sharing (phone-to-phone)
- Installation instructions for non-technical users

### 📝 Nice to Have (Post-Workshop)

- Bluetooth mesh fallback implementation
- Background sync service with foreground notification
- Battery optimization
- Sync status UI
- Conflict resolution UI
- APK signing for release builds

## How to Complete This

### Immediate Next Steps (< 1 hour):

1. **Install Java 11+**
   ```bash
   brew install openjdk@17
   ```

2. **Build APK**
   ```bash
   cd frontend
   npx vite build
   npx cap sync android
   cd android
   export JAVA_HOME=$(/usr/libexec/java_home -v 17)
   ./gradlew assembleDebug
   ```

3. **Test APK**
   ```bash
   # Install on device via adb
   adb install android/app/build/outputs/apk/debug/app-debug.apk

   # Or transfer APK and install manually
   ```

### Follow-up Work (1-2 days):

4. **Fix Local Storage Types**
   - Read `frontend/src/types/valueflows.ts` carefully
   - Update `local-api.ts` to match exact field names
   - Re-enable in `App.tsx`

5. **Implement DTN Sync**
   - Create DTN bundle from sync_queue table
   - Send via WiFi Direct sockets
   - Receive and apply on other device

6. **Create Distribution Method**
   - Generate QR code linking to APK
   - Or: Implement mesh-based APK sharing

## Testing Checklist

Once APK is built:

- [ ] APK installs on Android 8+ device
- [ ] App launches successfully
- [ ] Can view existing data (fetched from API when online)
- [ ] WiFi Direct permission requests appear
- [ ] Can discover nearby peers (requires 2+ devices)
- [ ] Mesh network status shows correctly

## Files Created/Modified

### Created:
- `frontend/capacitor.config.ts`
- `frontend/android/` (entire Android project)
- `frontend/android/app/src/main/java/org/solarpunk/mesh/MeshNetworkPlugin.java`
- `frontend/android/app/src/main/java/org/solarpunk/mesh/WiFiDirectBroadcastReceiver.java`
- `frontend/src/plugins/mesh-network.ts`
- `frontend/src/plugins/mesh-network-web.ts`

### Modified:
- `frontend/android/app/src/main/AndroidManifest.xml` - Added permissions
- `frontend/android/variables.gradle` - Set minSdkVersion = 26

### Started (Not Yet Integrated):
- `frontend/src/storage/sqlite.ts` - SQLite database wrapper
- `frontend/src/storage/local-api.ts` - Local-first API implementation
- `frontend/src/api/adaptive-valueflows.ts` - Online/offline API switcher

## Architecture Notes

### Current State
- Frontend builds and syncs to Android project
- Native WiFi Direct plugin ready (untested - needs APK build)
- App will run but currently requires internet for API calls

### Target State (After Completion)
- App stores all data locally in SQLite
- Works completely offline
- Syncs with nearby peers via WiFi Direct
- Queues changes for propagation through mesh

### Migration Path
1. Build and test basic APK (app works with internet)
2. Add local storage layer (app works offline)
3. Add sync mechanism (app shares data via mesh)
4. Test at workshop with 200+ devices

## Known Issues

1. **Java Version**: System has Java 8, needs 11+
2. **TypeScript Errors**: Pre-existing errors in ExchangesPage.tsx (provider_completed fields)
3. **Type Mismatches**: Local storage layer types don't match ValueFlows definitions
4. **Untested Native Code**: WiFi Direct plugin not yet tested on actual device

## Success Criteria Met

- [x] Capacitor project initialized
- [x] Android platform added
- [x] Minimum SDK version set to Android 8.0
- [x] Mesh networking permissions configured
- [x] WiFi Direct native plugin implemented
- [ ] APK builds successfully (BLOCKED: Java version)
- [ ] App installs on Android 8+ device (BLOCKED: No APK yet)
- [ ] App works in airplane mode (BLOCKED: Local storage not integrated)
- [ ] Two phones sync via WiFi Direct (BLOCKED: Sync not implemented)

## Recommendation

**Priority 1 (Workshop Blocker):**
- Install Java 11+ and build APK
- Get basic app running on phones
- Local storage can wait if API server available at workshop

**Priority 2 (Week 1 Post-Workshop):**
- Fix local storage types
- Integrate local-first data layer
- Implement mesh sync

**Priority 3 (Month 1):**
- Production APK signing
- Bluetooth fallback
- Battery optimization
