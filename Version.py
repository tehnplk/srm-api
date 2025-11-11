PROJECT = "HisHelp"
CODE = "9"
NAME = "1.0.7"
RELEASE = "2025-11-11"

__all__ = ["PROJECT", "CODE", "NAME", "RELEASE"]


if __name__ == "__main__":
    import requests
    import json

    url = "https://script.google.com/macros/s/AKfycbxD9CI91jGbL-MWHvBDvCqgh8s9DaTEZ38ItvX7yX37w65mQzWC_DQ5SzlrViEooh9wtg/exec"

    # POST
    payload = {
        "new_version_code": CODE,
        "new_version_name": NAME,
        "new_version_release": RELEASE,
    }
    resp = requests.post(url, json=payload)
    print(resp.json())
