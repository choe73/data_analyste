"""Datasets endpoint tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_datasets(client: AsyncClient):
    """Test listing datasets."""
    response = await client.get("/api/v1/datasets")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_list_datasets_with_pagination(client: AsyncClient):
    """Test listing datasets with pagination parameters."""
    response = await client.get("/api/v1/datasets?skip=0&limit=10")
    assert response.status_code == 200
