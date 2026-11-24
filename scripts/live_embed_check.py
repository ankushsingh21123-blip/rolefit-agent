"""Live embedding check via the registered custom.gemini connection.

Posts one :embedContent call for a job text through the same surrogate
mechanism the connector helper uses, and prints only the embedding
dimension. No key is read or printed. For local verification only —
the app itself reads GEMINI_API_KEY from the environment at runtime.
"""

import json
import os
import sys
import urllib.request

sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
from dynamic_credentials import add_surrogate_to_request, read_json_response

HOST = "generativelanguage.googleapis.com"
CONNECTION = "custom.gemini"


def main() -> int:
    url = f"https://{HOST}/v1beta/models/gemini-embedding-001:embedContent"
    body = {
        "content": {
            "parts": [
                {
                    "text": "Backend Engineer (Python, Remote) at Nimbus Cloud. "
                    "Fully remote backend role: Python services, FastAPI APIs "
                    "and Postgres schemas for a cloud storage product."
                }
            ]
        }
    }
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(), method="POST",
        headers={"Content-Type": "application/json"},
    )
    add_surrogate_to_request(req, CONNECTION, allowed_hosts=[HOST])
    with urllib.request.build_opener().open(req, timeout=60) as resp:
        data = read_json_response(resp)
    values = data["embedding"]["values"]
    print(f"embedding ok: dim={len(values)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
