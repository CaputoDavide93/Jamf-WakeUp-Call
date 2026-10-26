"""A tiny stand-in for the parts of Jamf Pro that wake-up-call talks to.

Demo data only: made-up computers, serials and people. It answers the same
paths the client calls, with the response shapes of the Jamf Pro Classic API
and the Jamf Pro API. It is a screenshot and docs fixture, not a Jamf emulator.

Computer 103 refuses the redeploy with a 500 so a failure can be shown.
"""
from __future__ import annotations

import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

COMPUTERS = {
    101: ("demo-mac-01", "DEMO0000101", "Alex Example", "Designer"),
    102: ("demo-mac-02", "DEMO0000102", "Sam Sample", "Engineer"),
    103: ("demo-mac-03", "DEMO0000103", "Robin Placeholder", "Analyst"),
    104: ("demo-mac-04", "DEMO0000104", "Jo Demo", "Support"),
}
GROUP_ID = "42"
TOKEN = "demo-token"


def computer_record(cid: int) -> dict:
    name, serial, real_name, position = COMPUTERS[cid]
    return {
        "computer": {
            "general": {"id": cid, "name": name, "serial_number": serial},
            "location": {
                "username": real_name.split()[0].lower(),
                "real_name": real_name,
                "position": position,
            },
        }
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # keep the terminal quiet
        pass

    def _send(self, status: int, body: dict) -> None:
        raw = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _authed(self) -> bool:
        return self.headers.get("Authorization") == f"Bearer {TOKEN}"

    def do_GET(self):
        if not self._authed():
            return self._send(401, {"error": "unauthorized"})
        if self.path == f"/JSSResource/computergroups/id/{GROUP_ID}":
            members = [{"id": cid, "name": c[0]} for cid, c in COMPUTERS.items()]
            return self._send(200, {"computer_group": {"computers": members}})
        m = re.fullmatch(r"/JSSResource/computers/id/(\d+)", self.path)
        if m and int(m[1]) in COMPUTERS:
            return self._send(200, computer_record(int(m[1])))
        m = re.fullmatch(r"/JSSResource/computers/serialnumber/(\w+)", self.path)
        if m:
            for cid, c in COMPUTERS.items():
                if c[1] == m[1]:
                    return self._send(200, computer_record(cid))
        return self._send(404, {"error": "not found"})

    def do_POST(self):
        if not self._authed():
            return self._send(401, {"error": "unauthorized"})
        m = re.fullmatch(r"/api/v1/jamf-management-framework/redeploy/(\d+)", self.path)
        if not m or int(m[1]) not in COMPUTERS:
            return self._send(404, {"error": "not found"})
        cid = int(m[1])
        if cid == 103:
            return self._send(500, {"error": "server error"})
        return self._send(
            200, {"deviceId": str(cid), "commandUuid": f"00000000-0000-0000-0000-{cid:012d}"}
        )


def serve(port: int = 8099) -> ThreadingHTTPServer:
    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


if __name__ == "__main__":
    server = serve()
    print("mock Jamf on http://127.0.0.1:8099 (group 42, token demo-token)")
    server.serve_forever()
