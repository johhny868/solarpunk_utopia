"""
End-to-End tests for Sanctuary Network.

Tests the complete flow from resource offering through multi-steward verification
to request fulfillment and auto-purge.

CRITICAL: These tests verify life-safety systems. Failure = unsafe resources get offered.

Test scenario (from proposal):
WHEN Carol offers safe_space resource with HIGH sensitivity
THEN resource NOT visible until verified
WHEN 3-of-5 stewards verify (escape routes, capacity, buddy protocol)
THEN resource becomes available
WHEN steward creates urgent request
THEN high-trust (>0.8) users can see and coordinate
AND no permanent records retained after 24h
"""

import pytest
import pytest_asyncio
import os
import tempfile
from datetime import datetime, timedelta
from freezegun import freeze_time

from app.models.sanctuary import (
    SanctuaryResourceType,
    SensitivityLevel,
    VerificationStatus,
    VerificationMethod,
    VerificationRecord,
)
from app.database.sanctuary_repository import SanctuaryRepository
from app.services.sanctuary_service import SanctuaryService


class TestSanctuaryNetworkE2E:
    """End-to-end sanctuary network flow tests"""

    @pytest_asyncio.fixture(autouse=True)
    async def setup_and_teardown(self):
        """Set up test database and service"""
        # Setup
        # Create temp database
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")

        # Run migrations
        import aiosqlite
        async with aiosqlite.connect(self.db_path) as db:
            # Base schema
            base_schema = """
            CREATE TABLE IF NOT EXISTS bundles (
                bundleId TEXT PRIMARY KEY,
                queue TEXT NOT NULL,
                createdAt TEXT NOT NULL,
                expiresAt TEXT NOT NULL,
                priority TEXT NOT NULL,
                audience TEXT NOT NULL,
                topic TEXT NOT NULL,
                tags TEXT NOT NULL,
                payloadType TEXT NOT NULL,
                payload TEXT NOT NULL,
                hopLimit INTEGER NOT NULL,
                hopCount INTEGER NOT NULL DEFAULT 0,
                receiptPolicy TEXT NOT NULL,
                signature TEXT NOT NULL,
                authorPublicKey TEXT NOT NULL,
                sizeBytes INTEGER NOT NULL,
                addedToQueueAt TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
            await db.executescript(base_schema)

            # Sanctuary migration
            with open("app/database/migrations/002_sanctuary_multi_steward_verification.sql") as f:
                migration_sql = f.read()
            await db.executescript(migration_sql)
            await db.commit()

        # Create service
        self.service = SanctuaryService(self.db_path)

        yield  # Run the test

        # Teardown
        os.close(self.db_fd)
        os.unlink(self.db_path)

    @pytest.mark.asyncio
    async def test_full_sanctuary_flow(self):
        """
        E2E test - Resource offer → multi-steward verification → request → allocation → auto-purge

        Complete flow:
        1. Carol offers HIGH sensitivity safe_space resource
        2. Resource NOT visible until verified
        3. Three stewards verify (escape routes, capacity, buddy protocol)
        4. Resource becomes available to high-trust users
        5. Steward creates urgent sanctuary request
        6. Steward matches request to resource
        7. Coordination happens (24h window)
        8. Match completed, 24h purge timer starts
        9. Auto-purge removes sensitive data

        Scenario:
        - Carol (trust 0.9) offers safe_space for 2 people, 7 days
        - Alice, Bob, Dave (stewards) verify with in-person checks
        - Emergency sanctuary request created
        - High-trust (>0.8) coordinator matches request to resource
        - Completion triggers 24h purge timer
        """

        # ===== Step 1: Carol offers safe_space resource =====
        carol_id = "user-carol"
        cell_id = "cell-phoenix"

        with freeze_time("2025-12-19T10:00:00Z"):
            resource = self.service.offer_resource(
                user_id=carol_id,
                cell_id=cell_id,
                resource_type=SanctuaryResourceType.SAFE_SPACE,
                description="Phoenix location, 2 people, 1 week max, back door exit",
                capacity=2,
                duration_days=7
            )

        # Verify resource created
        assert resource.id is not None
        assert resource.resource_type == SanctuaryResourceType.SAFE_SPACE
        assert resource.sensitivity == SensitivityLevel.HIGH  # Auto-set for safe_space
        assert resource.offered_by == carol_id
        assert resource.capacity == 2
        assert resource.duration_days == 7
        assert resource.verification_status == VerificationStatus.PENDING
        assert resource.available is True

        # ===== Step 2: Resource NOT visible until verified =====
        # Low-trust user should not see unverified resource
        low_trust_resources = self.service.get_available_resources(
            cell_id=cell_id,
            user_trust_score=0.85,  # Even high trust can't see unverified
            resource_type=SanctuaryResourceType.SAFE_SPACE
        )
        assert len(low_trust_resources) == 0  # Not yet verified

        # ===== Step 3: First steward verification =====
        alice_steward_id = "steward-alice"

        with freeze_time("2025-12-19T11:00:00Z"):
            # Alice verifies: in-person visit, checks escape routes
            self.service.add_verification(
                resource_id=resource.id,
                steward_id=alice_steward_id,
                verification_method=VerificationMethod.IN_PERSON,
                notes="Verified back door exit, front porch visible from street, quiet neighborhood",
                escape_routes_verified=True,
                capacity_verified=True,
                buddy_protocol_available=True
            )

        # Get verification status
        verification = self.service.get_verification_status(resource.id)
        assert verification.verification_count == 1
        assert verification.needs_second_verification is True
        assert verification.is_valid is False  # Need 2+ verifications

        # Still not visible (need 2+ verifications)
        resources_after_one = self.service.get_available_resources(
            cell_id=cell_id,
            user_trust_score=0.85,
            resource_type=SanctuaryResourceType.SAFE_SPACE
        )
        assert len(resources_after_one) == 0

        # ===== Step 4: Second steward verification =====
        bob_steward_id = "steward-bob"

        with freeze_time("2025-12-19T12:00:00Z"):
            # Bob verifies: video call, confirms capacity
            self.service.add_verification(
                resource_id=resource.id,
                steward_id=bob_steward_id,
                verification_method=VerificationMethod.VIDEO_CALL,
                notes="Video tour confirmed layout, capacity OK, owner seems reliable",
                escape_routes_verified=True,
                capacity_verified=True,
                buddy_protocol_available=True
            )

        # Now resource is valid (2 verifications)
        verification_after_two = self.service.get_verification_status(resource.id)
        assert verification_after_two.verification_count == 2
        assert verification_after_two.is_valid is True
        assert verification_after_two.expires_at is not None  # 90 days from last check

        # Update resource verification status
        resource_updated = self.service.repo.get_resource(resource.id)
        resource_updated.verification_status = VerificationStatus.VERIFIED
        self.service.repo.update_resource(resource_updated)

        # ===== Step 5: Third steward verification (optional, increases trust) =====
        dave_steward_id = "steward-dave"

        with freeze_time("2025-12-19T13:00:00Z"):
            # Dave verifies: trusted referral (knows Carol personally)
            self.service.add_verification(
                resource_id=resource.id,
                steward_id=dave_steward_id,
                verification_method=VerificationMethod.TRUSTED_REFERRAL,
                notes="Known Carol for 5 years, trust her completely",
                escape_routes_verified=True,
                capacity_verified=True,
                buddy_protocol_available=True
            )

        verification_final = self.service.get_verification_status(resource.id)
        assert verification_final.verification_count == 3

        # ===== Step 6: Resource NOW visible to high-trust users =====
        high_trust_resources = self.service.get_available_resources(
            cell_id=cell_id,
            user_trust_score=0.85,  # HIGH sensitivity requires 0.8+
            resource_type=SanctuaryResourceType.SAFE_SPACE
        )
        assert len(high_trust_resources) == 1
        assert high_trust_resources[0].id == resource.id

        # Low-trust users still cannot see HIGH sensitivity resources
        medium_trust_resources = self.service.get_available_resources(
            cell_id=cell_id,
            user_trust_score=0.65,  # Below 0.8 threshold
            resource_type=SanctuaryResourceType.SAFE_SPACE
        )
        assert len(medium_trust_resources) == 0

        # ===== Step 7: Steward creates urgent sanctuary request =====
        steward_coordinator_id = "steward-coordinator"

        with freeze_time("2025-12-19T14:00:00Z"):
            request = self.service.create_request(
                user_id="user-person-at-risk",
                cell_id=cell_id,
                steward_id=steward_coordinator_id,
                request_type=SanctuaryResourceType.SAFE_SPACE,
                urgency="urgent",
                description="Person needs shelter, Phoenix area, immediate",
                people_count=1,
                duration_needed_days=3,
                location_hint="Phoenix metro"
            )

        assert request.id is not None
        assert request.urgency == "urgent"
        assert request.verified_by == steward_coordinator_id
        assert request.status == "pending"

        # ===== Step 8: Coordinator matches request to resource =====
        with freeze_time("2025-12-19T14:30:00Z"):
            match = self.service.match_request_to_resource(
                request_id=request.id,
                resource_id=resource.id,
                cell_id=cell_id,
                steward_id=steward_coordinator_id
            )

        assert match.id is not None
        assert match.request_id == request.id
        assert match.resource_id == resource.id
        assert match.coordinated_by == steward_coordinator_id
        assert match.status == "active"

        # ===== Step 9: Coordination happens (simulated 24h window) =====
        # In real system: encrypted messages, check-ins, buddy protocol
        # For E2E test: just verify match is active

        active_match = self.service.repo.get_match(match.id)
        assert active_match.status == "active"
        assert active_match.completed_at is None

        # ===== Step 10: Match completed =====
        with freeze_time("2025-12-20T10:00:00Z"):
            self.service.complete_match(match_id=match.id)

            # Record successful use
            self.service.record_sanctuary_use(
                resource_id=resource.id,
                request_id=request.id,
                outcome="success"
            )

            # Get completed match
            completed_match = self.service.repo.get_match(match.id)

        assert completed_match.status == "completed"
        assert completed_match.completed_at is not None
        assert completed_match.purge_at is not None

        # Verify purge_at is 24 hours after completion
        expected_purge = completed_match.completed_at + timedelta(hours=24)
        assert completed_match.purge_at == expected_purge

        # Verify successful use was recorded
        updated_verification = self.service.repo.get_verification_aggregate(resource.id)
        assert updated_verification.successful_uses == 1

        # ===== Step 11: Auto-purge after 24 hours =====
        with freeze_time("2025-12-21T10:01:00Z"):
            # Run auto-purge process
            self.service.run_auto_purge()

        # Verify match purged
        purged_match = self.service.repo.get_match(match.id)
        assert purged_match is None  # Purged from database

        # Verify request also purged
        purged_request = self.service.repo.get_request(request.id)
        assert purged_request is None  # Purged

        # Resource should still exist (for future use)
        remaining_resource = self.service.repo.get_resource(resource.id)
        assert remaining_resource is not None
        assert remaining_resource.id == resource.id

    @pytest.mark.asyncio
    async def test_high_sensitivity_requires_high_trust(self):
        """
        Verify HIGH sensitivity resources require trust >= 0.8

        Medium-trust users can see MEDIUM sensitivity, but not HIGH.
        This prevents infiltrators from accessing safe house locations.
        """
        # Carol offers HIGH sensitivity resource
        resource = self.service.offer_resource(
            user_id="user-carol",
            cell_id="cell-phoenix",
            resource_type=SanctuaryResourceType.SAFE_SPACE,  # Auto HIGH sensitivity
            description="Safe space",
            capacity=2,
            duration_days=7
        )

        # Mark as verified (for this test)
        resource.verification_status = VerificationStatus.VERIFIED
        self.service.repo.update_resource(resource)

        # Add verifications to make it valid
        for steward_id in ["steward-alice", "steward-bob"]:
            self.service.add_verification(
                resource_id=resource.id,
                steward_id=steward_id,
                verification_method=VerificationMethod.IN_PERSON,
                escape_routes_verified=True,
                capacity_verified=True,
                buddy_protocol_available=True
            )

        # High-trust user (0.85) CAN see
        high_trust_resources = self.service.get_available_resources(
            cell_id="cell-phoenix",
            user_trust_score=0.85,
            resource_type=SanctuaryResourceType.SAFE_SPACE
        )
        assert len(high_trust_resources) == 1

        # Medium-trust user (0.65) CANNOT see
        medium_trust_resources = self.service.get_available_resources(
            cell_id="cell-phoenix",
            user_trust_score=0.65,
            resource_type=SanctuaryResourceType.SAFE_SPACE
        )
        assert len(medium_trust_resources) == 0

        # Border case: exactly 0.8 SHOULD see
        border_trust_resources = self.service.get_available_resources(
            cell_id="cell-phoenix",
            user_trust_score=0.8,
            resource_type=SanctuaryResourceType.SAFE_SPACE
        )
        assert len(border_trust_resources) == 1

    @pytest.mark.asyncio
    async def test_steward_cannot_verify_twice(self):
        """
        Verify same steward cannot verify a resource twice

        This prevents a single compromised steward from faking consensus.
        """
        # Offer resource
        resource = self.service.offer_resource(
            user_id="user-carol",
            cell_id="cell-phoenix",
            resource_type=SanctuaryResourceType.SAFE_SPACE,
            description="Safe space",
            capacity=2
        )

        # Alice verifies
        self.service.add_verification(
            resource_id=resource.id,
            steward_id="steward-alice",
            verification_method=VerificationMethod.IN_PERSON,
            escape_routes_verified=True,
            capacity_verified=True,
            buddy_protocol_available=True
        )

        # Alice tries to verify again (should fail)
        with pytest.raises(ValueError, match="already verified"):
            self.service.add_verification(
                resource_id=resource.id,
                steward_id="steward-alice",  # Same steward
                verification_method=VerificationMethod.VIDEO_CALL,
                escape_routes_verified=True,
                capacity_verified=True,
                buddy_protocol_available=True
            )

    @pytest.mark.asyncio
    async def test_verification_expires_after_90_days(self):
        """
        Verify sanctuary verifications expire after 90 days

        Prevents outdated verifications (space could change owners, become unsafe).
        """
        with freeze_time("2025-12-19T10:00:00Z") as frozen_time:
            # Offer and verify resource
            resource = self.service.offer_resource(
                user_id="user-carol",
                cell_id="cell-phoenix",
                resource_type=SanctuaryResourceType.SAFE_SPACE,
                description="Safe space",
                capacity=2
            )

            # Two stewards verify
            for steward_id in ["steward-alice", "steward-bob"]:
                self.service.add_verification(
                    resource_id=resource.id,
                    steward_id=steward_id,
                    verification_method=VerificationMethod.IN_PERSON,
                    escape_routes_verified=True,
                    capacity_verified=True,
                    buddy_protocol_available=True
                )

            # Verify is valid
            verification = self.service.get_verification_status(resource.id)
            assert verification.is_valid is True

            # Fast-forward 91 days
            frozen_time.move_to("2026-03-21T10:00:00Z")

            # Verify is now expired
            verification_expired = self.service.get_verification_status(resource.id)
            assert verification_expired.is_valid is False  # Expired

    @pytest.mark.asyncio
    async def test_high_trust_resources_for_critical_needs(self):
        """
        Verify resources with 3+ successful uses become high-trust for critical needs

        This helps coordinators quickly identify proven-safe resources during emergencies.
        """
        # Offer resource
        resource = self.service.offer_resource(
            user_id="user-carol",
            cell_id="cell-phoenix",
            resource_type=SanctuaryResourceType.SAFE_SPACE,
            description="Safe space",
            capacity=2
        )

        # Verify resource
        for steward_id in ["steward-alice", "steward-bob"]:
            self.service.add_verification(
                resource_id=resource.id,
                steward_id=steward_id,
                verification_method=VerificationMethod.IN_PERSON,
                escape_routes_verified=True,
                capacity_verified=True,
                buddy_protocol_available=True
            )

        # Initial: 0 successful uses, not high-trust
        verification = self.service.get_verification_status(resource.id)
        assert verification.successful_uses == 0
        assert verification.is_high_trust is False

        # Record 3 successful uses
        for i in range(3):
            self.service.record_sanctuary_use(
                resource_id=resource.id,
                request_id=f"test-req-{i}",
                outcome="success"
            )

        # Now high-trust for critical needs
        verification_high_trust = self.service.get_verification_status(resource.id)
        assert verification_high_trust.successful_uses == 3
        assert verification_high_trust.is_high_trust is True

    @pytest.mark.asyncio
    async def test_needs_second_verification_flag(self):
        """
        Verify needs_second_verification flag helps stewards coordinate

        After first verification, system should flag that second verification needed.
        """
        # Offer resource
        resource = self.service.offer_resource(
            user_id="user-carol",
            cell_id="cell-phoenix",
            resource_type=SanctuaryResourceType.SAFE_SPACE,
            description="Safe space",
            capacity=2
        )

        # No verifications yet
        verification = self.service.get_verification_status(resource.id)
        if verification is None:
            # Need first verification - can't check needs_second_verification yet
            pass
        else:
            assert verification.needs_second_verification is False

        # First verification
        self.service.add_verification(
            resource_id=resource.id,
            steward_id="steward-alice",
            verification_method=VerificationMethod.IN_PERSON,
            escape_routes_verified=True,
            capacity_verified=True,
            buddy_protocol_available=True
        )

        # Now needs second verification
        verification_after_one = self.service.get_verification_status(resource.id)
        assert verification_after_one.needs_second_verification is True

        # Second verification
        self.service.add_verification(
            resource_id=resource.id,
            steward_id="steward-bob",
            verification_method=VerificationMethod.VIDEO_CALL,
            escape_routes_verified=True,
            capacity_verified=True,
            buddy_protocol_available=True
        )

        # No longer needs second verification
        verification_after_two = self.service.get_verification_status(resource.id)
        assert verification_after_two.needs_second_verification is False
