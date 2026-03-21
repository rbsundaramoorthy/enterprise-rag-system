from __future__ import annotations

from fastapi.testclient import TestClient

from tests.support import make_token


def test_me_requires_authentication(test_app: tuple[TestClient, object, object]) -> None:
    client, _, _ = test_app
    response = client.get("/me")

    assert response.status_code == 401
    assert response.json() == {"detail": "Missing bearer token."}


def test_me_returns_principal_context(test_app: tuple[TestClient, object, object]) -> None:
    client, _, _ = test_app
    token = make_token(
        user_id="user-acme-1",
        tenant_id="tenant-acme",
        groups=["engineering"],
        roles=["member"],
    )

    response = client.get(
        "/me",
        headers={
            "Authorization": f"Bearer {token}",
            "X-Correlation-ID": "corr-123",
        },
    )

    assert response.status_code == 200
    assert response.headers["X-Correlation-ID"] == "corr-123"
    assert response.json() == {
        "user_id": "user-acme-1",
        "tenant_id": "tenant-acme",
        "groups": ["engineering"],
        "roles": ["member"],
        "correlation_id": "corr-123",
    }


def test_group_claim_parsing_accepts_csv_string(
    test_app: tuple[TestClient, object, object],
) -> None:
    client, _, _ = test_app
    token = make_token(
        user_id="user-acme-1",
        tenant_id="tenant-acme",
        groups="engineering, finance",
        roles="member, reviewer",
    )

    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["groups"] == ["engineering", "finance"]
    assert response.json()["roles"] == ["member", "reviewer"]


def test_document_listing_blocks_cross_tenant_access(
    test_app: tuple[TestClient, object, object],
) -> None:
    client, _, _ = test_app
    token = make_token(
        user_id="user-acme-1",
        tenant_id="tenant-acme",
        groups=["engineering"],
        roles=["member"],
    )

    response = client.get(
        "/v1/tenants/tenant-globex/documents",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Cross-tenant access is forbidden."}


def test_document_listing_returns_only_current_tenant_documents(
    test_app: tuple[TestClient, object, object],
) -> None:
    client, _, _ = test_app
    token = make_token(
        user_id="user-acme-1",
        tenant_id="tenant-acme",
        groups=["engineering"],
        roles=["member"],
    )

    response = client.get(
        "/v1/tenants/tenant-acme/documents",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": "doc-acme-1",
            "tenant_id": "tenant-acme",
            "title": "Acme Handbook",
            "source_type": "upload",
            "mime_type": "text/plain",
            "tags": ["handbook"],
            "status": "active",
            "created_by_user_id": "user-acme-1",
            "source_uri": "file://acme.pdf",
            "created_at": response.json()[0]["created_at"],
        }
    ]
