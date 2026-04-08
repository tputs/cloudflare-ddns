import requests
import logging
import sys

# ── Config ──────────────────────────────────────────────────────────────────
CONFIG_FILE = "/etc/cloudflare-ddns.conf"


def load_config(path: str) -> dict:
    """Load key=value config file, return as dict."""
    config = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, _, value = line.partition("=")
            config[key.strip()] = value.strip()
    return config


# ── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


# ── Functions ───────────────────────────────────────────────────────────────
IP_SERVICES = [
    "https://icanhazip.com",
    "https://api.ipify.org",
    "https://checkip.amazonaws.com",
]


def get_public_ip() -> str:
    """Return current public IP address."""
    for url in IP_SERVICES:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.text.strip()
        except requests.RequestException:
            log.warning("Failed to reach %s, trying next...", url)
    log.error("All IP services failed, cannot determine public IP")
    sys.exit(1)


def get_dns_ip(zone_id: str, record_id: str, api_token: str) -> str:
    """Return IP currently set on the Cloudflare DNS record."""
    url = (
        f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
    )
    headers = {"Authorization": f"Bearer {api_token}"}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json()["result"]["content"]


def update_dns_ip(
    zone_id: str, record_id: str, api_token: str, public_ip: str, record_name: str
) -> None:
    """Update the Cloudflare DNS record to the new IP."""
    url = (
        f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
    )
    headers = {"Authorization": f"Bearer {api_token}"}
    body = {
        "type": "A",
        "name": record_name,
        "content": public_ip,
        "ttl": 120,
    }
    response = requests.put(url, headers=headers, json=body, timeout=10)
    response.raise_for_status()


# ── Main ────────────────────────────────────────────────────────────────────
def main() -> None:
    try:
        config = load_config(CONFIG_FILE)
        api_token = config["api_token"]
        zone_id = config["zone_id"]
        record_id = config["record_id"]
        record_name = config["record_name"]
        public_ip = get_public_ip()
        dns_ip = get_dns_ip(zone_id, record_id, api_token)
        if public_ip == dns_ip:
            log.info("No change: %s", public_ip)
            return
        update_dns_ip(zone_id, record_id, api_token, public_ip, record_name)
        log.info("Updated DNS: %s -> %s", dns_ip, public_ip)
    except KeyError as e:
        log.error("Missing config key: %s", e)
        sys.exit(1)
    except requests.RequestException as e:
        log.error("API error: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
