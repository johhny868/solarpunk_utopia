# Solarpunk Phone Deployment System

Automated provisioning system for deploying Solarpunk mesh network on Android phones.

## Overview

This system provisions phones with:
- Solarpunk ValueFlows Node app (custom APK)
- F-Droid and community apps (Briar, Manyverse, Syncthing, Kiwix, etc.)
- Role-based configuration presets
- Offline content (for Library nodes)

**Target:** <15 minutes per phone, batch provisioning supported

## Quick Start

### Prerequisites

1. **Install adb** (Android Debug Bridge)
   ```bash
   # macOS
   brew install android-platform-tools

   # Linux
   sudo apt install adb

   # Verify
   adb version
   ```

2. **Prepare phones**
   - Install LineageOS or Android 8.0+ (API 26+)
   - Enable Developer Options: Settings → About → tap Build Number 7x
   - Enable USB Debugging: Settings → Developer Options → USB Debugging
   - Connect via USB
   - Authorize computer when prompted

3. **Build Solarpunk APK** (one-time)
   ```bash
   cd frontend
   npm install
   npm run build
   cd android
   ./gradlew assembleDebug
   ```

### Provision Single Phone

```bash
# Default (Citizen role)
./deployment/scripts/provision_phone.sh

# Specific role
./deployment/scripts/provision_phone.sh --role=bridge

# Specific device (if multiple connected)
./deployment/scripts/provision_phone.sh --role=library --serial=ABC123

# Skip optional steps
./deployment/scripts/provision_phone.sh --skip-apps --skip-content
```

### Provision Multiple Phones (Batch)

```bash
# Provision 10 citizen phones in parallel
./deployment/scripts/provision_batch.sh --role=citizen --count=10

# Provision 3 bridge phones, max 3 parallel
./deployment/scripts/provision_batch.sh --role=bridge --count=3 --parallel=3
```

### Test Provisioned Phone

```bash
# Test default device
./deployment/scripts/test_phone.sh

# Test specific device
./deployment/scripts/test_phone.sh --serial=ABC123
```

## Directory Structure

```
deployment/
├── README.md                          # This file
├── presets/                           # Role-based configurations
│   ├── citizen.json                   # Default (512MB cache, balanced battery)
│   ├── bridge.json                    # Bridge node (4GB cache, aggressive forwarding)
│   ├── ap.json                        # Access Point (hotspot, index publishing)
│   └── library.json                   # Library (20GB cache, knowledge hosting)
├── scripts/                           # Provisioning automation
│   ├── provision_phone.sh             # Single phone provisioning
│   ├── provision_batch.sh             # Batch provisioning
│   └── test_phone.sh                  # Validation tests
├── docs/                              # Documentation
│   ├── PARTICIPANT_QUICKSTART.md      # 1-page guide for participants
│   └── FACILITATOR_TROUBLESHOOTING.md # Troubleshooting for facilitators
├── apks/                              # Third-party APKs (gitignored)
│   └── FDroid.apk                     # Downloaded on first run
└── results/                           # Provisioning logs (gitignored)
    └── YYYYMMDD_HHMMSS/               # Timestamped batch results
```

## Role Presets

### Citizen (Default)
- **Use case:** Typical commune member
- **Cache:** 512MB
- **Battery:** Balanced (sync every 10 min)
- **Forwarding:** Emergency + perishable only
- **Speculative caching:** Disabled

### Bridge
- **Use case:** Carries bundles between AP islands
- **Cache:** 4GB
- **Battery:** Balanced (sync every 5 min)
- **Forwarding:** Aggressive for emergency/perishable
- **Speculative caching:** Enabled (emergency + hot bundles)

### AP (Access Point)
- **Use case:** Provides network infrastructure
- **Cache:** 4GB
- **Battery:** Performance (plugged in)
- **Hotspot:** Always on
- **Index publishing:** Every 5 min

### Library
- **Use case:** Knowledge hub with large storage
- **Cache:** 20GB
- **Battery:** Performance (plugged in required)
- **File serving:** Aggressive
- **Content:** Full Kiwix packs (permaculture, repair, health)

## What Gets Installed

### Base Apps (via F-Droid)
- **Briar** - Secure messaging, forums, blogs (DTN-ready)
- **Manyverse** - Scuttlebutt social feed (offline-first)
- **Syncthing** - File synchronization (peer-to-peer)
- **Kiwix** - Offline Wikipedia and knowledge packs
- **Organic Maps** - Offline navigation (OpenStreetMap)
- **Termux** - Terminal emulator (for advanced users)

### Custom Apps
- **Solarpunk ValueFlows Node** - Gift economy coordination
  - Offer/need creation and browsing
  - Match suggestions and exchange coordination
  - DTN bundle sync
  - Agent proposals

### Configuration
- Role-based preset (JSON file)
- Cache budgets and TTL policies
- Forwarding rules
- Battery profiles
- Network settings (WiFi Direct, mDNS, etc.)

## Provisioning Process

The `provision_phone.sh` script performs these steps:

1. **Check prerequisites** - adb, preset file, device connection
2. **Install F-Droid** - Download and install F-Droid APK
3. **Install base apps** - Briar, Manyverse, Syncthing, etc. (TODO: implement)
4. **Install custom APKs** - Solarpunk app (built from frontend/)
5. **Apply preset** - Push role configuration to device
6. **Load content** - Kiwix packs for Library nodes (TODO: implement)
7. **Validate** - Run tests (app installed, preset exists, battery >50%, storage >1GB)

**Expected duration:** 10-15 minutes per phone

## Batch Provisioning

The `provision_batch.sh` script:
- Gets list of connected devices via `adb devices`
- Provisions up to `--count` devices
- Runs `--parallel` provisions simultaneously (default: 5)
- Logs each provision to `results/TIMESTAMP/provision_SERIAL.log`
- Reports success/failure summary

**Use case:** Provision 20+ phones before workshop

## Testing

The `test_phone.sh` script validates:
- ✓ Device connected
- ✓ Android 8.0+ (SDK 26+)
- ✓ Solarpunk app installed
- ✓ Preset configuration exists
- ✓ Battery >50%
- ✓ Storage >500MB free
- ✓ WiFi enabled

**Exit code:** 0 if all tests pass, 1 otherwise

## Workshop Preparation

### Timeline: 1 Week Before

1. **Acquire phones** (20+ recommended)
   - Android 8.0+, 2GB RAM, 16GB storage
   - Used phones fine (cheaper = better for workshop)

2. **Install LineageOS** (if applicable)
   - Clean Android without Google dependencies
   - Enables advanced features (WiFi Direct, hotspot on any device)

3. **Build APKs**
   ```bash
   cd frontend
   npm run build
   cd android
   ./gradlew assembleDebug
   ```

4. **Test provisioning** on 2-3 phones
   ```bash
   ./deployment/scripts/provision_phone.sh --role=citizen
   ./deployment/scripts/test_phone.sh
   ```

### Timeline: 1 Day Before

5. **Batch provision all phones**
   ```bash
   # Example: 15 citizen, 3 bridge, 1 AP, 1 library
   ./deployment/scripts/provision_batch.sh --role=citizen --count=15
   ./deployment/scripts/provision_batch.sh --role=bridge --count=3
   ./deployment/scripts/provision_phone.sh --role=ap
   ./deployment/scripts/provision_phone.sh --role=library
   ```

6. **Validate all phones**
   ```bash
   for serial in $(adb devices | grep device$ | awk '{print $1}'); do
       ./deployment/scripts/test_phone.sh --serial=$serial || echo "FAILED: $serial"
   done
   ```

7. **Label phones**
   - SP-Citizen-01 through SP-Citizen-15
   - SP-Bridge-01 through SP-Bridge-03
   - SP-AP-01
   - SP-Library-01

8. **Charge to >80%**

9. **Print guides**
   - 30x Participant Quick Start (deployment/docs/PARTICIPANT_QUICKSTART.md)
   - 5x Facilitator Troubleshooting (deployment/docs/FACILITATOR_TROUBLESHOOTING.md)

### Timeline: Workshop Day

10. **Set up APs** in different areas (garden, kitchen, workshop, library)

11. **Distribute phones** to participants with quick-start guide

12. **Support** using Facilitator Troubleshooting guide

## TODO / Future Enhancements

- [ ] Implement actual base app installation (currently stubbed)
- [ ] Implement content loading for Library nodes (Kiwix ZIM files, maps)
- [ ] Add support for F-Droid repo management (add custom repos)
- [ ] Build release APK (signed) instead of debug
- [ ] Add preset configuration via adb shell broadcast (if app supports)
- [ ] Create web dashboard for batch provisioning progress
- [ ] Support for custom phone labels (printed QR codes)
- [ ] Automated testing of mesh connectivity (simulate workshop scenario)

## Troubleshooting

See `deployment/docs/FACILITATOR_TROUBLESHOOTING.md` for comprehensive troubleshooting guide.

### Common Issues

**Problem:** `adb devices` shows "unauthorized"
- **Fix:** Check phone screen for authorization prompt, tap "Always allow"

**Problem:** APK not found
- **Fix:** Build APK: `cd frontend/android && ./gradlew assembleDebug`

**Problem:** Phone shows "Insufficient storage"
- **Fix:** Clear cache: Settings → Storage → Free up space

**Problem:** Provisioning times out
- **Fix:** Check USB cable (use data cable, not charge-only), restart adb: `adb kill-server && adb start-server`

## Architecture Compliance

This system adheres to **ARCHITECTURE_CONSTRAINTS.md**:

- ✓ **Old phones:** Targets Android 8.0+ (2017), 2GB RAM
- ✓ **Fully distributed:** No server dependencies, peer-to-peer sync
- ✓ **Works offline:** Local-first, mesh propagation
- ✓ **No big tech:** F-Droid only, no Google Play dependency
- ✓ **Seizure resistant:** Bundles expire, compartmentalized data

## License

This deployment system is part of the Solarpunk Gift Economy Mesh Network project.

## Credits

- Provisioning scripts: Claude (Anthropic)
- Preset configurations: Based on solarpunk_node_full_spec.md
- Android app: See frontend/README.md

---

**Version:** 1.0
**Status:** Initial implementation (some features stubbed for future completion)
**Updated:** 2025-12-19
