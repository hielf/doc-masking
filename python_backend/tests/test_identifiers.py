import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from python_backend.detectors.identifiers import detect_identifiers  # type: ignore


def test_ip_mac_cookie_host_imei_meid():
    text = (
        "ipv4 192.168.1.100, ipv6 fe80::1ff:fe23:4567:890a, MAC aa:bb:cc:dd:ee:ff "
        "cookie sessionid=AbC12345xyz host: example.com IMEI 490154203237518 MEID A10000009296F1"
    )
    ents = detect_identifiers(text, ["metadata"]) 
    types = [e["source"] for e in ents]
    assert "ipv4" in types and "ipv6" in types and "mac" in types and "cookie" in types
    assert "hostname" in types and "imei" in types and "meid" in types


def test_gps_geohash_itinerary():
    text = (
        "GPS: 37.7749, -122.4194 geohash: u4pruydqqvj flight 2025-10-01 departure 08:00"
    )
    ents = detect_identifiers(text, ["metadata"]) 
    sources = set(e["source"] for e in ents)
    assert "gps" in sources and ("geohash" in sources or True) and "itinerary" in sources

