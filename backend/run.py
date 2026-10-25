"""Start the private local API and display the ephemeral token for the creator."""

import os
import secrets

import uvicorn


def main():
    token = os.environ.setdefault("PUZZLEMINT_TOKEN", secrets.token_urlsafe(32))
    print(f"PuzzleMint local session token: {token}", flush=True)
    print("Bind address: http://127.0.0.1:8765", flush=True)
    uvicorn.run("app.main:app", host="127.0.0.1", port=8765, app_dir=os.path.dirname(__file__))


if __name__ == "__main__":
    main()
