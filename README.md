# cloudflare-ddns

A lightweight Python script to keep a Cloudflare DNS A record in sync with your home IP address. Designed to run as a systemd timer on a Linux host.

## Requirements

- Python 3.12+
- `requests` library

## Configuration

Create `/etc/cloudflare-ddns.conf`:

```
api_token=your_cloudflare_api_token
zone_id=your_zone_id
record_id=your_record_id
record_name=yourdomain.com
```

The API token needs DNS Edit permissions for your zone.

## Usage
```bash
pip install -r requirements.txt
python ddns.py
```

## Deployment

Designed to be deployed via Ansible with a systemd timer for periodic execution.
