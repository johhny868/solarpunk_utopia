"""
Tests for API Endpoint Fixes (GAP-65, GAP-69, GAP-71, GAP-72)

Tests fix-api-endpoints proposal implementation:
- Match accept/reject endpoints
- Commitments CRUD endpoints
- Listing deletion ownership check (documented for future)
- Proposal rejection auth fix
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime


class TestMatchAcceptReject:
    """Tests for GAP-65: Match accept/reject endpoints"""

    def test_accept_endpoint_exists(self):
        """Verify /matches/{id}/accept endpoint exists"""
        from valueflows_node.app.api.vf.matches import accept_match
        assert accept_match is not None

    def test_reject_endpoint_exists(self):
        """Verify /matches/{id}/reject endpoint exists"""
        from valueflows_node.app.api.vf.matches import reject_match
        assert reject_match is not None

    @pytest.mark.asyncio
    async def test_accept_match_updates_status(self):
        """Verify accept changes match status to accepted"""
        from valueflows_node.app.api.vf.matches import accept_match
        from valueflows_node.app.models.vf.match import Match, MatchStatus

        # Mock database and repository
        with patch('valueflows_node.app.api.vf.matches.get_database') as mock_db:
            mock_conn = Mock()
            mock_db.return_value.conn = mock_conn

            with patch('valueflows_node.app.api.vf.matches.MatchRepository') as mock_repo_class:
                mock_repo = Mock()
                mock_repo_class.return_value = mock_repo

                # Create test match
                test_match = Match(
                    id="match:test",
                    offer_id="offer:1",
                    need_id="need:1",
                    provider_id="agent:1",
                    receiver_id="agent:2",
                    status=MatchStatus.SUGGESTED,
                    created_at=datetime.now()
                )

                mock_repo.find_by_id.return_value = test_match
                mock_repo.update.return_value = test_match

                with patch('valueflows_node.app.api.vf.matches.VFBundlePublisher') as mock_publisher:
                    mock_publisher.return_value.publish_vf_object.return_value = {"bundleId": "bundle:1"}

                    result = await accept_match("match:test")

                    assert result["status"] == "accepted"
                    assert mock_repo.update.called

    @pytest.mark.asyncio
    async def test_reject_match_updates_status(self):
        """Verify reject changes match status to rejected"""
        from valueflows_node.app.api.vf.matches import reject_match
        from valueflows_node.app.models.vf.match import Match, MatchStatus

        with patch('valueflows_node.app.api.vf.matches.get_database') as mock_db:
            mock_conn = Mock()
            mock_db.return_value.conn = mock_conn

            with patch('valueflows_node.app.api.vf.matches.MatchRepository') as mock_repo_class:
                mock_repo = Mock()
                mock_repo_class.return_value = mock_repo

                test_match = Match(
                    id="match:test",
                    offer_id="offer:1",
                    need_id="need:1",
                    provider_id="agent:1",
                    receiver_id="agent:2",
                    status=MatchStatus.SUGGESTED,
                    created_at=datetime.now()
                )

                mock_repo.find_by_id.return_value = test_match
                mock_repo.update.return_value = test_match

                with patch('valueflows_node.app.api.vf.matches.VFBundlePublisher') as mock_publisher:
                    mock_publisher.return_value.publish_vf_object.return_value = {"bundleId": "bundle:1"}

                    result = await reject_match("match:test", "not interested")

                    assert result["status"] == "rejected"
                    assert result["reason"] == "not interested"


class TestCommitmentsEndpoint:
    """Tests for GAP-69: Commitments endpoint"""

    def test_commitments_router_exists(self):
        """Verify commitments router exists"""
        from valueflows_node.app.api.vf.commitments import router
        assert router is not None
        assert router.prefix == "/vf/commitments"

    def test_get_commitments_endpoint_exists(self):
        """Verify GET /commitments endpoint exists"""
        from valueflows_node.app.api.vf.commitments import get_commitments
        assert get_commitments is not None

    def test_create_commitment_endpoint_exists(self):
        """Verify POST /commitments endpoint exists"""
        from valueflows_node.app.api.vf.commitments import create_commitment
        assert create_commitment is not None

    def test_get_commitment_by_id_endpoint_exists(self):
        """Verify GET /commitments/{id} endpoint exists"""
        from valueflows_node.app.api.vf.commitments import get_commitment
        assert get_commitment is not None

    def test_update_commitment_endpoint_exists(self):
        """Verify PATCH /commitments/{id} endpoint exists"""
        from valueflows_node.app.api.vf.commitments import update_commitment
        assert update_commitment is not None

    def test_delete_commitment_endpoint_exists(self):
        """Verify DELETE /commitments/{id} endpoint exists"""
        from valueflows_node.app.api.vf.commitments import delete_commitment
        assert delete_commitment is not None

    @pytest.mark.asyncio
    async def test_get_commitments_returns_list(self):
        """Verify GET /commitments returns commitments list"""
        from valueflows_node.app.api.vf.commitments import get_commitments
        from valueflows_node.app.models.vf.commitment import Commitment, CommitmentStatus

        with patch('valueflows_node.app.api.vf.commitments.get_database') as mock_db:
            mock_conn = Mock()
            mock_db.return_value.conn = mock_conn

            with patch('valueflows_node.app.api.vf.commitments.CommitmentRepository') as mock_repo_class:
                mock_repo = Mock()
                mock_repo_class.return_value = mock_repo

                test_commitments = [
                    Commitment(
                        id="commitment:1",
                        agent_id="agent:1",
                        action="deliver",
                        status=CommitmentStatus.ACCEPTED
                    ),
                    Commitment(
                        id="commitment:2",
                        agent_id="agent:1",
                        action="work",
                        status=CommitmentStatus.PROPOSED
                    )
                ]

                mock_repo.find_by_agent.return_value = test_commitments

                result = await get_commitments(agent_id="agent:1")

                assert "commitments" in result
                assert result["count"] == 2


class TestListingDeletion:
    """Tests for GAP-71: Listing deletion ownership verification"""

    def test_listing_delete_has_ownership_todo(self):
        """Verify delete endpoint has GAP-71 TODO for ownership check"""
        from valueflows_node.app.api.vf.listings import delete_listing
        import inspect

        source = inspect.getsource(delete_listing)
        assert "GAP-71" in source, "Delete endpoint should document GAP-71 ownership check"
        assert "TODO" in source, "Delete endpoint should have TODO for ownership verification"

    @pytest.mark.asyncio
    async def test_listing_delete_works(self):
        """Verify delete endpoint exists and executes"""
        from valueflows_node.app.api.vf.listings import delete_listing

        with patch('valueflows_node.app.api.vf.listings.get_database') as mock_db:
            mock_conn = Mock()
            mock_db.return_value.conn = mock_conn

            with patch('valueflows_node.app.api.vf.listings.ListingRepository') as mock_repo_class:
                mock_repo = Mock()
                mock_repo_class.return_value = mock_repo

                from valueflows_node.app.models.vf.listing import Listing, ListingType
                test_listing = Listing(
                    id="listing:1",
                    agent_id="agent:1",
                    listing_type=ListingType.OFFER,
                    resource_spec_id="spec:1"
                )

                mock_repo.find_by_id.return_value = test_listing
                mock_repo.delete.return_value = True

                result = await delete_listing("listing:1")

                assert result is None  # 204 No Content
                assert mock_repo.delete.called


class TestProposalRejection:
    """Tests for GAP-72: Proposal rejection endpoint user_id fix"""

    def test_reject_proposal_has_auth_dependency(self):
        """Verify reject endpoint uses auth dependency"""
        from app.api.agents import reject_proposal
        import inspect

        signature = inspect.signature(reject_proposal)
        params = signature.parameters

        assert "current_user" in params, "Reject endpoint should have current_user parameter"

    def test_reject_proposal_uses_current_user_id(self):
        """Verify reject endpoint uses current_user.id not request.user_id"""
        from app.api.agents import reject_proposal
        import inspect

        source = inspect.getsource(reject_proposal)
        assert "current_user.id" in source, "Should use current_user.id"
        assert "request.user_id" not in source, "Should NOT use request.user_id"
        assert "GAP-72" in source, "Should document GAP-72 fix"


def test_commitments_router_registered():
    """Verify commitments router is registered in main app"""
    from valueflows_node.app.main import app

    # Check router is included
    route_paths = [route.path for route in app.routes]
    commitment_routes = [p for p in route_paths if "/vf/commitments" in p]

    assert len(commitment_routes) > 0, "Commitments router should be registered"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
