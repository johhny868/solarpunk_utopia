# Facilitator Troubleshooting Guide

Quick reference for common issues during workshop and deployment.

## Pre-Workshop Setup

### Phone Won't Connect to adb
**Symptoms:** `adb devices` shows no devices or "unauthorized"

**Fix:**
1. Enable USB debugging: Settings → Developer Options → USB Debugging
2. If "Developer Options" hidden: Settings → About Phone → tap Build Number 7 times
3. Check USB cable (some are power-only)
4. On phone, tap "Always allow from this computer" when prompt appears
5. Retry: `adb kill-server && adb start-server && adb devices`

### Provisioning Script Fails
**Symptoms:** Script exits with error

**Diagnosis:**
```bash
# Check logs
cat deployment/results/LATEST/provision_SERIAL.log

# Common issues:
# - Storage full: adb shell df /sdcard
# - Low battery: adb shell dumpsys battery
# - Wrong Android version: adb shell getprop ro.build.version.sdk
```

**Fix:**
- Storage: Clear /sdcard/Download and /sdcard/DCIM/Camera
- Battery: Charge phone to >50%
- Android version: Phone must be Android 8.0+ (SDK 26+)

### APK Build Fails
**Symptoms:** `frontend/android/app/build/outputs/apk/` empty

**Fix:**
```bash
cd frontend
npm install
npm run build
cd android
./gradlew clean
./gradlew assembleDebug
# APK should appear in app/build/outputs/apk/debug/
```

---

## Workshop Day Issues

### Participant Can't Find Solarpunk App
**Fix:**
1. Check app drawer (swipe up from home screen)
2. If missing: Settings → Apps → show all → look for "Solarpunk"
3. If truly missing: Re-run provisioning for that device

### Phone Won't Connect to AP
**Symptoms:** WiFi connected but no mesh sync

**Fix:**
1. Settings → WiFi → forget network → reconnect
2. Check AP is broadcasting (SSIDPrefix "Solarpunk")
3. Verify phone within range (walk closer to AP area)
4. Check WiFi isn't disabled by battery saver

### Offer/Need Doesn't Appear for Others
**Symptoms:** Person creates offer, others don't see it after 5+ minutes

**Diagnosis:**
```bash
# Check if bundle was created
adb -s DEVICE_SERIAL shell cat /sdcard/solarpunk/preset.json

# Check DTN service status
adb -s DEVICE_SERIAL shell dumpsys activity services | grep solarpunk
```

**Fix:**
1. Ensure WiFi enabled and connected
2. Wait 5-10 min (mesh propagation takes time)
3. Walk phone near a bridge node or AP
4. Check if bundle TTL expired (perishables: 48h, check created time)

### Battery Draining Too Fast
**Symptoms:** Phone loses >20% per hour

**Diagnosis:**
Check role:
```bash
adb -s DEVICE_SERIAL shell cat /sdcard/solarpunk/preset.json | grep role
```

**Fix:**
- **Citizen role:** Should sync every 10 min. Check for rogue apps.
- **Bridge role:** Higher usage is expected. Advise participant to charge more often.
- **AP role:** Must stay plugged in.
- Generic: Settings → Battery → check usage by app

### Match Accepted But No Notification
**Symptoms:** Two people matched but one didn't get notified

**Fix:**
1. Have both participants manually refresh in app
2. Check notification permissions: Settings → Apps → Solarpunk → Notifications → Enabled
3. Mesh may have delayed delivery - wait 2-3 min and refresh

---

## Advanced Troubleshooting

### Check Logs on Device
```bash
# Android system logs
adb -s SERIAL logcat -d > device_log.txt

# Filter for Solarpunk app
adb -s SERIAL logcat -d | grep -i solarpunk

# Check DTN bundle stats
adb -s SERIAL shell cat /sdcard/solarpunk/dtn_stats.json
```

### Reset Phone to Provisioned State
```bash
# Option 1: Clear app data (keeps preset)
adb -s SERIAL shell pm clear org.solarpunk.mesh

# Option 2: Uninstall and re-provision
adb -s SERIAL uninstall org.solarpunk.mesh
./deployment/scripts/provision_phone.sh --serial=SERIAL --role=citizen

# Option 3: Factory reset (last resort)
# Have participant: Settings → System → Reset → Factory data reset
# Then re-provision from scratch
```

### Verify Mesh Connectivity
```bash
# Check WiFi Direct status
adb -s SERIAL shell dumpsys wifi | grep -i "direct"

# Check nearby devices
adb -s SERIAL shell dumpsys wifi | grep -i "peer"

# Ping another device (if on same AP)
adb -s SERIAL shell ping -c 3 10.44.1.X
```

---

## Common Questions

### "Why can't I see offers from people far away?"
**Answer:** The mesh is local-first. Bundles propagate when bridge nodes walk between areas. If someone is across town, it may take time for bundles to reach you. This is intentional - it prioritizes local coordination and reduces internet dependency.

### "Can I use this at home / outside the commune?"
**Answer:** Yes! Install the APK on your own phone. You'll need either:
1. A local AP to connect to, OR
2. WiFi Direct to connect peer-to-peer, OR
3. To act as a bridge between locations

It works anywhere people gather.

### "What happens if my phone is seized?"
**Answer:**
- Panic features (duress PIN, quick wipe) if configured
- Bundles auto-expire (perishables in 48h)
- Sensitive data auto-purges after time window
- Web of trust prevents network-wide compromise from one device

### "How do I add more people after the workshop?"
**Answer:**
1. Install APK on their phone (via QR code, file share, or Syncthing)
2. Have them scan event QR (if available) or join via invitation
3. Vouch for them in web of trust (if you know them)
4. They'll sync bundles automatically once connected to mesh

---

## Emergency Contacts

### During Workshop
- **Lead Facilitator:** [Name/Radio channel]
- **Tech Support:** [Name/Radio channel]
- **Medical:** [Location]

### Post-Workshop
- **Mesh Issues:** Post in #tech-help Briar forum
- **Safety Concerns:** Contact local cell steward
- **Critical Bugs:** GitHub issues (if internet available)

---

## Phone Roles Reference

| Role | Cache | Battery | Use Case |
|------|-------|---------|----------|
| **Citizen** | 512MB | Balanced | Default for participants |
| **Bridge** | 4GB | Higher usage | Carries bundles between APs |
| **AP** | 4GB | Plugged in | Provides network infrastructure |
| **Library** | 20GB | Plugged in | Hosts knowledge, large files |

---

## Validation Checklist

Use before handing phone to participant:

- [ ] Solarpunk app installed and launches
- [ ] Preset file exists at /sdcard/solarpunk/preset.json
- [ ] Battery >50% (ideally >80%)
- [ ] Storage >1GB free
- [ ] WiFi enabled
- [ ] Test: Create offer → appears in browse view
- [ ] Phone labeled with role and number (e.g., "SP-Citizen-01")

---

**Version:** 1.0
**Updated:** 2025-12-19
**For:** Workshop Facilitators
