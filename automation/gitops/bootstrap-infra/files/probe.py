"""Report one reference tenant's access to its assigned workshop canary."""
import http.client
import json
import os
from pathlib import Path
import ssl


def canary_status(namespace):
    status, service = api_get(namespace, "services/workshop-netcheck", read_service=True)
    if status != 200:
        return None, f"service_lookup_{status}"
    spec = service["spec"]
    address = spec.get("clusterIP")
    if (spec.get("type") != "ClusterIP" or address in (None, "", "None") or
            spec.get("selector") != {"app": "workshop-netcheck"} or
            not any(p["port"] == 8080 and p.get("protocol", "TCP") == "TCP"
                    for p in spec.get("ports", []))):
        return None, "unexpected_service"
    conn = http.client.HTTPConnection(address, 8080, timeout=3)
    try:
        try:
            conn.connect()
        except TimeoutError:
            return address, "connect_timeout"
        conn.request("GET", "/")
        return address, str(conn.getresponse().status)
    except (OSError, http.client.HTTPException) as exc:
        return address, type(exc).__name__
    finally:
        conn.close()


def api_get(namespace, resource, read_service=False):
    account = Path("/var/run/secrets/kubernetes.io/serviceaccount")
    tls = ssl.create_default_context(cafile=str(account / "ca.crt"))
    conn = http.client.HTTPSConnection("kubernetes.default.svc", context=tls, timeout=5)
    try:
        token = (account / "token").read_text().strip()
        conn.request("GET", f"/api/v1/namespaces/{namespace}/{resource}",
                     headers={"Authorization": f"Bearer {token}"})
        response = conn.getresponse()
        body = json.load(response) if read_service and response.status == 200 else None
        return response.status, body
    except (OSError, http.client.HTTPException) as exc:
        return type(exc).__name__, None
    finally:
        conn.close()


if __name__ == "__main__":
    target = os.environ["TARGET_NAMESPACE"]
    ip, network = canary_status(target)
    api_status, _ = api_get(target, "configmaps/national-parks-gitops-info")
    print(json.dumps({"namespace": target, "serviceIP": ip, "http": network,
                      "configMapHTTP": api_status}), flush=True)
