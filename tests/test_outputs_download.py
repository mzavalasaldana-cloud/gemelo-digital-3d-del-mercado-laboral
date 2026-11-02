import pytest
from fastapi.testclient import TestClient
from backend.main import app, _scan_output_images

client = TestClient(app)


def test_scan_output_images_finds_files():
    images = _scan_output_images()
    assert len(images) >= 4
    rel_paths = [img["relativePath"] for img in images]
    assert "figure4_calibration.png" in rel_paths
    assert "figure5_sanctions_sweep.png" in rel_paths
    assert "figure6_trajectories.png" in rel_paths
    assert "figure7_policy_effects.png" in rel_paths


def test_api_list_output_images():
    res = client.get("/api/v1/outputs/images")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["total"] >= 4
    assert len(data["categories"]) >= 3
    assert len(data["images"]) == data["total"]


def test_api_download_output_image():
    res = client.get("/api/v1/outputs/download-image?path=figure4_calibration.png")
    assert res.status_code == 200
    assert "image/png" in res.headers["content-type"]
    assert "attachment" in res.headers.get("content-disposition", "")
    assert len(res.content) > 10000


def test_api_download_output_image_path_traversal_blocked():
    res = client.get("/api/v1/outputs/download-image?path=../../etc/passwd")
    assert res.status_code in (400, 404)


def test_api_download_all_zip():
    res = client.get("/api/v1/outputs/download-all-zip")
    assert res.status_code == 200
    assert "application/zip" in res.headers["content-type"]
    assert "attachment" in res.headers.get("content-disposition", "")
    assert len(res.content) > 50000
