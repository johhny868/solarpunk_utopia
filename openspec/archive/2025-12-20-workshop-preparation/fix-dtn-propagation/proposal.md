# Proposal: Fix DTN Bundle Propagation - Make Mesh Actually Work

**Submitted By:** Gap Analysis Agent
**Date:** 2025-12-19
**Status:** ✅ IMPLEMENTED
**Gaps Addressed:** GAP-110, GAP-113, GAP-117
**Priority:** P0 - Before Workshop
**Implemented:** 2025-12-19

## Problem Statement

Multiple features claim to use DTN (Delay-Tolerant Networking) for mesh propagation but return placeholder bundle IDs without actually creating or propagating bundles.

1. **GAP-110**: Rapid Response alerts never propagate via mesh
2. **GAP-113**: Panic burn notices never reach the network
3. **GAP-117**: Mesh messages stored locally but never sent

The entire premise of a mesh network that works without internet is broken.

## Current State (Broken)

### Rapid Response (`app/services/rapid_response_service.py:128`)
```python
# TODO: Actually create and propagate the bundle
return f"bundle-alert-{alert.id}"  # Placeholder!
```
**Risk:** Emergency alerts only reach people connected to same node.

### Burn Notice (`app/services/panic_service.py:187`)
```python
# TODO: Integrate with bundle service to propagate via DTN
# TODO: Create DTN bundle with burn notice
```
**Risk:** Compromised identity continues to be trusted by network.

### Mesh Messages (`app/api/messages.py:144`)
```python
# TODO: Create DTN bundle for mesh delivery
```
**Risk:** Messages only work when sender and recipient are on same node.

## Proposed Solution

### 1. Bundle Service Integration

Create a unified DTN bundle creation interface:

```python
from app.services.bundle_service import BundleService
from dtn.bundle import Bundle, BundleFlags

class MeshPropagator:
    """Unified mesh propagation for all message types"""

    def __init__(self, bundle_service: BundleService):
        self.bundle_service = bundle_service

    async def propagate_alert(self, alert: Alert) -> str:
        """Create and propagate emergency alert bundle"""
        bundle = Bundle(
            destination="dtn://mesh/alerts",  # Multicast to all nodes
            payload=alert.to_bytes(),
            flags=BundleFlags.PRIORITY_EXPEDITED | BundleFlags.CUSTODY_REQUESTED,
            lifetime_seconds=3600 * 24,  # 24 hour TTL
        )
        bundle_id = await self.bundle_service.create_and_store(bundle)
        await self.bundle_service.queue_for_propagation(bundle_id)
        return bundle_id

    async def propagate_burn_notice(self, burn_notice: BurnNotice) -> str:
        """Create and propagate burn notice bundle"""
        bundle = Bundle(
            destination="dtn://mesh/trust/revocations",
            payload=burn_notice.to_bytes(),
            flags=BundleFlags.PRIORITY_EXPEDITED,
            lifetime_seconds=3600 * 24 * 7,  # 7 day TTL for trust updates
        )
        bundle_id = await self.bundle_service.create_and_store(bundle)
        await self.bundle_service.queue_for_propagation(bundle_id)
        return bundle_id

    async def propagate_message(self, message: Message, recipient_node: str) -> str:
        """Create and propagate encrypted message bundle"""
        bundle = Bundle(
            destination=f"dtn://{recipient_node}/inbox",
            payload=message.encrypted_content,
            flags=BundleFlags.DELIVERY_REPORT_REQUESTED,
            lifetime_seconds=3600 * 24 * 3,  # 3 day TTL
        )
        bundle_id = await self.bundle_service.create_and_store(bundle)
        await self.bundle_service.queue_for_propagation(bundle_id)
        return bundle_id
```

### 2. Update Rapid Response Service

```python
# app/services/rapid_response_service.py

async def _propagate_alert(self, alert: Alert) -> str:
    """Actually propagate alert via DTN mesh"""
    propagator = MeshPropagator(self.bundle_service)
    bundle_id = await propagator.propagate_alert(alert)

    # Also trigger local WiFi Direct broadcast for immediate neighbors
    await self.wifi_direct_service.broadcast_emergency(alert)

    return bundle_id
```

### 3. Update Panic Service

```python
# app/services/panic_service.py

async def _broadcast_burn_notice(self, user_id: str) -> str:
    """Actually broadcast burn notice to network"""
    burn_notice = BurnNotice(
        user_id=user_id,
        issued_at=datetime.utcnow(),
        signed_by=self._get_current_user_signature(),
    )

    propagator = MeshPropagator(self.bundle_service)
    bundle_id = await propagator.propagate_burn_notice(burn_notice)

    return bundle_id
```

### 4. Update Message API

```python
# app/api/messages.py

@router.post("/send")
async def send_message(request: SendMessageRequest):
    # ... encryption code ...

    # Store locally
    message = await message_repo.create(...)

    # Propagate via mesh
    propagator = MeshPropagator(bundle_service)
    bundle_id = await propagator.propagate_message(
        message,
        recipient_node=request.recipient_node
    )

    return {"message_id": message.id, "bundle_id": bundle_id, "status": "queued"}
```

## Requirements

### SHALL Requirements
- SHALL create actual DTN bundles for all mesh communications
- SHALL queue bundles for propagation to neighboring nodes
- SHALL use WiFi Direct for immediate neighbor broadcast of emergencies
- SHALL support store-and-forward for offline recipients
- SHALL track bundle delivery status

### MUST Requirements
- MUST work when internet is unavailable
- MUST propagate within 30 seconds to immediate neighbors
- MUST handle network partitions gracefully

## Testing

```python
def test_alert_creates_real_bundle():
    """Verify alerts create actual DTN bundles"""
    alert = create_test_alert()
    bundle_id = await rapid_response.propagate_alert(alert)

    # Should be real bundle in bundle store
    bundle = await bundle_service.get(bundle_id)
    assert bundle is not None
    assert bundle.destination == "dtn://mesh/alerts"
    assert alert.id in bundle.payload.decode()

def test_message_propagates_offline():
    """Verify messages propagate without internet"""
    # Disable internet
    with network_disabled():
        message_id = await send_message(recipient, content)

        # Should still be queued
        bundle = await get_pending_bundles()
        assert len(bundle) > 0
```

## Files to Modify

1. `app/services/rapid_response_service.py:128, 272, 316`
2. `app/services/panic_service.py:187, 201, 223-224`
3. `app/api/messages.py:144`
4. New: `app/services/mesh_propagator.py`

## Dependencies

- Existing `BundleService` in codebase
- WiFi Direct service (existing)

## Effort Estimate

- 3-4 hours implementation
- 2 hours integration testing
- 1 hour mesh simulation testing

## Success Criteria

- [ ] Alerts propagate to all connected nodes within 30 seconds
- [ ] Burn notices reach 80% of network within 1 hour
- [ ] Messages deliver to offline recipients when they reconnect
- [ ] No placeholder bundle IDs in codebase
- [ ] All TODO comments in affected files resolved
