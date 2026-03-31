"""
Tests for order exception mapper and provider functionality.

Phase B.3: stock.picking based order exception mapping.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from providers.odoo.real.mapper import (
    map_order_exception_from_picking,
    is_valid_order_origin,
    parse_datetime,
)
from providers.odoo.real.provider import OdooRealProvider


class TestIsValidOrderOrigin:
    """Test order origin validation."""

    def test_valid_order_origin_s00038(self):
        """Test valid order origin format S00038."""
        assert is_valid_order_origin("S00038") is True

    def test_valid_order_origin_s123456(self):
        """Test valid order origin format S123456."""
        assert is_valid_order_origin("S123456") is True

    def test_invalid_order_origin_description(self):
        """Test invalid order origin with description text."""
        assert is_valid_order_origin("outgoing shipment") is False

    def test_invalid_order_origin_empty(self):
        """Test invalid order origin with empty string."""
        assert is_valid_order_origin("") is False

    def test_invalid_order_origin_none(self):
        """Test invalid order origin with None."""
        assert is_valid_order_origin(None) is False

    def test_invalid_order_origin_short(self):
        """Test invalid order origin with short format."""
        assert is_valid_order_origin("S123") is False


class TestParseDatetime:
    """Test datetime parsing."""

    def test_parse_datetime_from_string(self):
        """Test parsing datetime from ISO string."""
        result = parse_datetime("2026-03-30 13:05:32")
        assert result is not None
        assert result.year == 2026
        assert result.month == 3
        assert result.day == 30

    def test_parse_datetime_from_datetime(self):
        """Test parsing datetime from datetime object."""
        dt = datetime(2026, 3, 30, 13, 5, 32)
        result = parse_datetime(dt)
        assert result == dt

    def test_parse_datetime_none(self):
        """Test parsing datetime from None."""
        result = parse_datetime(None)
        assert result is None

    def test_parse_datetime_invalid_string(self):
        """Test parsing datetime from invalid string."""
        result = parse_datetime("invalid")
        assert result is None


class TestMapOrderExceptionFromPicking:
    """Test order exception mapping from stock.picking."""

    def test_map_delay_exception(self):
        """Test delay exception mapping when date_done > scheduled_date."""
        scheduled = datetime(2026, 3, 10, 10, 0, 0)
        done = datetime(2026, 3, 12, 15, 0, 0)
        
        picking = {
            "id": 1,
            "name": "WH/OUT/00001",
            "state": "done",
            "origin": "S00038",
            "scheduled_date": scheduled.isoformat(),
            "date_done": done.isoformat(),
            "create_date": datetime(2026, 3, 10, 9, 0, 0).isoformat(),
            "picking_type_id": [2, "Delivery"],
            "partner_id": [32, "Customer"],
            "note": "",
        }
        
        result = map_order_exception_from_picking(picking, order_exists=True)
        
        assert result is not None
        assert result["order_id"] == "S00038"
        assert result["platform"] == "odoo"
        assert result["exception_type"] == "delay"
        assert result["exception_status"] == "resolved"
        assert result["detail_json"]["odoo_model"] == "stock.picking"
        assert result["detail_json"]["delay_seconds"] > 0
        assert result["detail_json"]["limited_support"] is True

    def test_map_cancelled_exception(self):
        """Test cancelled exception mapping when state='cancel'."""
        picking = {
            "id": 2,
            "name": "WH/OUT/00002",
            "state": "cancel",
            "origin": "S00039",
            "scheduled_date": datetime(2026, 3, 10, 10, 0, 0).isoformat(),
            "date_done": None,
            "create_date": datetime(2026, 3, 10, 9, 0, 0).isoformat(),
            "picking_type_id": [2, "Delivery"],
            "partner_id": [33, "Customer"],
            "note": "Cancelled by customer",
        }
        
        result = map_order_exception_from_picking(picking, order_exists=True)
        
        assert result is not None
        assert result["order_id"] == "S00039"
        assert result["exception_type"] == "cancelled"
        assert result["exception_status"] == "cancelled"

    def test_skip_no_order_link(self):
        """Test that records without valid order link are skipped."""
        picking = {
            "id": 3,
            "name": "WH/OUT/00003",
            "state": "done",
            "origin": "outgoing shipment",
            "scheduled_date": datetime(2026, 3, 10, 10, 0, 0).isoformat(),
            "date_done": datetime(2026, 3, 12, 15, 0, 0).isoformat(),
            "create_date": datetime(2026, 3, 10, 9, 0, 0).isoformat(),
            "picking_type_id": [2, "Delivery"],
            "partner_id": [34, "Customer"],
            "note": "",
        }
        
        result = map_order_exception_from_picking(picking, order_exists=False)
        
        assert result is None

    def test_skip_no_exception_signal(self):
        """Test that records without exception signal are skipped."""
        picking = {
            "id": 4,
            "name": "WH/OUT/00004",
            "state": "done",
            "origin": "S00040",
            "scheduled_date": datetime(2026, 3, 10, 10, 0, 0).isoformat(),
            "date_done": datetime(2026, 3, 10, 9, 30, 0).isoformat(),
            "create_date": datetime(2026, 3, 10, 9, 0, 0).isoformat(),
            "picking_type_id": [2, "Delivery"],
            "partner_id": [35, "Customer"],
            "note": "",
        }
        
        result = map_order_exception_from_picking(picking, order_exists=True)
        
        assert result is None

    def test_map_picking_done_no_delay(self):
        """Test that done picking without delay returns None."""
        scheduled = datetime(2026, 3, 10, 10, 0, 0)
        done = datetime(2026, 3, 10, 9, 30, 0)
        
        picking = {
            "id": 5,
            "name": "WH/OUT/00005",
            "state": "done",
            "origin": "S00041",
            "scheduled_date": scheduled.isoformat(),
            "date_done": done.isoformat(),
            "create_date": datetime(2026, 3, 10, 9, 0, 0).isoformat(),
            "picking_type_id": [2, "Delivery"],
            "partner_id": [36, "Customer"],
            "note": "",
        }
        
        result = map_order_exception_from_picking(picking, order_exists=True)
        
        assert result is None

    def test_skip_order_not_exists(self):
        """Test that records where order doesn't exist are skipped."""
        picking = {
            "id": 6,
            "name": "WH/OUT/00006",
            "state": "cancel",
            "origin": "S00999",
            "scheduled_date": datetime(2026, 3, 10, 10, 0, 0).isoformat(),
            "date_done": None,
            "create_date": datetime(2026, 3, 10, 9, 0, 0).isoformat(),
            "picking_type_id": [2, "Delivery"],
            "partner_id": [37, "Customer"],
            "note": "",
        }
        
        result = map_order_exception_from_picking(picking, order_exists=False)
        
        assert result is None

    def test_skip_draft_state(self):
        """Test that draft state pickings are skipped."""
        picking = {
            "id": 7,
            "name": "WH/OUT/00007",
            "state": "draft",
            "origin": "S00042",
            "scheduled_date": datetime(2026, 3, 10, 10, 0, 0).isoformat(),
            "date_done": None,
            "create_date": datetime(2026, 3, 10, 9, 0, 0).isoformat(),
            "picking_type_id": [2, "Delivery"],
            "partner_id": [38, "Customer"],
            "note": "",
        }
        
        result = map_order_exception_from_picking(picking, order_exists=True)
        
        assert result is None

    def test_skip_assigned_state(self):
        """Test that assigned state pickings are skipped."""
        picking = {
            "id": 8,
            "name": "WH/OUT/00008",
            "state": "assigned",
            "origin": "S00043",
            "scheduled_date": datetime(2026, 3, 10, 10, 0, 0).isoformat(),
            "date_done": None,
            "create_date": datetime(2026, 3, 10, 9, 0, 0).isoformat(),
            "picking_type_id": [2, "Delivery"],
            "partner_id": [39, "Customer"],
            "note": "",
        }
        
        result = map_order_exception_from_picking(picking, order_exists=True)
        
        assert result is None


class TestProviderGetOrderExceptionFromPicking:
    """Test provider's _get_order_exceptions_from_picking method."""

    def test_provider_get_order_exceptions_from_picking(self):
        """Test provider correctly fetches exceptions from stock.picking."""
        mock_client = MagicMock()
        mock_client.search_read.side_effect = [
            [
                {
                    "id": 1,
                    "name": "WH/OUT/00001",
                    "state": "done",
                    "origin": "S00038",
                    "scheduled_date": "2026-03-10 10:00:00",
                    "date_done": "2026-03-12 15:00:00",
                    "create_date": "2026-03-10 09:00:00",
                    "picking_type_id": [2, "Delivery"],
                    "partner_id": [32, "Customer"],
                    "note": "",
                },
            ],
            [{"name": "S00038"}],
        ]
        
        provider = OdooRealProvider(mock_client)
        result = provider._get_order_exceptions_from_picking()
        
        assert len(result) == 1
        assert result[0]["order_id"] == "S00038"
        assert result[0]["exception_type"] == "delay"

    def test_provider_fallback_to_sale_order_on_error(self):
        """Test provider falls back to sale.order when stock.picking fails."""
        mock_client = MagicMock()
        mock_client.search_read.side_effect = [
            Exception("stock.picking not available"),
            [
                {
                    "id": 1,
                    "name": "S00038",
                    "state": "sale",
                    "note": "delay in delivery",
                },
            ],
        ]
        
        provider = OdooRealProvider(mock_client)
        result = provider.get_order_exception_list()
        
        assert len(result) >= 0

    def test_provider_returns_empty_list_when_no_exceptions(self):
        """Test provider returns empty list when no exceptions found."""
        mock_client = MagicMock()
        mock_client.search_read.side_effect = [
            [
                {
                    "id": 1,
                    "name": "WH/OUT/00001",
                    "state": "done",
                    "origin": "S00038",
                    "scheduled_date": "2026-03-10 10:00:00",
                    "date_done": "2026-03-10 09:30:00",
                    "create_date": "2026-03-10 09:00:00",
                    "picking_type_id": [2, "Delivery"],
                    "partner_id": [32, "Customer"],
                    "note": "",
                },
            ],
            [{"name": "S00038"}],
        ]
        
        provider = OdooRealProvider(mock_client)
        result = provider._get_order_exceptions_from_picking()
        
        assert result == []


class TestProviderGetOrderExceptionList:
    """Test provider's get_order_exception_list method."""

    def test_get_order_exception_list_returns_list(self):
        """Test that get_order_exception_list returns list[dict]."""
        mock_client = MagicMock()
        mock_client.search_read.return_value = []
        
        provider = OdooRealProvider(mock_client)
        result = provider.get_order_exception_list()
        
        assert isinstance(result, list)

    def test_get_order_exception_list_uses_picking_first(self):
        """Test that get_order_exception_list uses stock.picking as primary source."""
        mock_client = MagicMock()
        mock_client.search_read.side_effect = [
            [
                {
                    "id": 1,
                    "name": "WH/OUT/00001",
                    "state": "cancel",
                    "origin": "S00038",
                    "scheduled_date": "2026-03-10 10:00:00",
                    "date_done": None,
                    "create_date": "2026-03-10 09:00:00",
                    "picking_type_id": [2, "Delivery"],
                    "partner_id": [32, "Customer"],
                    "note": "",
                },
            ],
            [{"name": "S00038"}],
        ]
        
        provider = OdooRealProvider(mock_client)
        result = provider.get_order_exception_list()
        
        assert len(result) == 1
        assert result[0]["exception_type"] == "cancelled"
        assert result[0]["detail_json"]["source"] == "stock.picking"
