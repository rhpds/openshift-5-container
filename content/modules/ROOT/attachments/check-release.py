"""Check a student's Gitea revision, Argo CD sync and live workload evidence."""
import argparse
import json
import os
import re
import subprocess
import sys
import time


WEATHER = "quay.io/openshift-workshop-applications/weathernow:"
PATHS = {"national-parks-settings": "national-parks", "weathernow-lab": "weathernow"}


def run(*args):
    result = subprocess.run(args, text=True, capture_output=True, timeout=30,
                            env={**os.environ, "GIT_TERMINAL_PROMPT": "0"})
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or f"{args[0]} failed")
    return result.stdout.strip()


def get(namespace, kind, *args):
    return json.loads(run("oc", "get", kind, *args, "-n", namespace, "-o", "json",
                          "--request-timeout=10s"))


def owned_by(resource, uid):
    return any(ref["uid"] == uid and ref.get("controller")
               for ref in resource["metadata"].get("ownerReferences", []))


def current_pods(namespace, deployment):
    revision_key = "deployment.kubernetes.io/revision"
    revision = deployment["metadata"].get("annotations", {}).get(revision_key)
    if not revision:
        return []
    replicasets = get(namespace, "replicasets", "-l", "app=weathernow")["items"]
    owners = {rs["metadata"]["uid"] for rs in replicasets
              if owned_by(rs, deployment["metadata"]["uid"])
              and rs["metadata"].get("annotations", {}).get(revision_key) == revision}
    return [pod for pod in get(namespace, "pods", "-l", "app=weathernow")["items"]
            if not pod["metadata"].get("deletionTimestamp")
            and any(owned_by(pod, uid) for uid in owners)]


def fault_evidence(namespace, pod, container_status, mode):
    if mode == "readiness-fault":
        if pod["status"].get("phase") != "Running" or container_status.get("ready") is not False:
            return None
    else:
        reason = container_status.get("state", {}).get("waiting", {}).get("reason")
        if reason not in ("ErrImagePull", "ImagePullBackOff"):
            return None
    uid = pod["metadata"]["uid"]
    events = get(namespace, "events", "--field-selector", f"involvedObject.uid={uid}")["items"]
    for event in events:
        message = event.get("message", "")
        if mode == "readiness-fault":
            matches = event.get("reason") == "Unhealthy" and "readiness" in message.lower() and "18080" in message
        else:
            matches = event.get("reason") in ("Failed", "BackOff") and WEATHER + "module05-intentional-bad-tag" in message
        if (matches and event.get("type") == "Warning" and
                event.get("involvedObject", {}).get("uid") == uid):
            name = pod["metadata"]["name"]
            evidence = f'{name} {event["reason"]}: {message}'
            if mode == "readiness-fault":
                evidence += (f"\n  oc logs -n {namespace} pod/{name} -c weathernow --timestamps --tail=30"
                             f"\n  oc adm top pod -n {namespace} {name} --containers")
            return evidence
    return None


def matches_weather_template(pod_spec, image, readiness_port):
    container = next((c for c in pod_spec["containers"] if c["name"] == "weathernow"), {})
    return (container.get("image") == image and
            container.get("readinessProbe", {}).get("tcpSocket", {}).get("port") == readiness_port and
            any(p.get("name") == "http" and p.get("containerPort") == 8080
                for p in container.get("ports", [])))


def weather_evidence(namespace, mode, health):
    dep = get(namespace, "deployment/weathernow")
    spec, status = dep["spec"], dep.get("status", {})
    if status.get("observedGeneration") != dep["metadata"]["generation"]:
        return None
    expected_port = 18080 if mode == "readiness-fault" else "http"
    expected_image = WEATHER + ("module05-intentional-bad-tag" if mode == "image-fault" else "latest")
    if not matches_weather_template(spec["template"]["spec"], expected_image, expected_port):
        return None
    for pod in current_pods(namespace, dep):
        if not matches_weather_template(pod["spec"], expected_image, expected_port):
            continue
        state = next((c for c in pod.get("status", {}).get("containerStatuses", [])
                      if c["name"] == "weathernow"), {})
        if mode != "healthy":
            evidence = fault_evidence(namespace, pod, state, mode)
            if evidence:
                return evidence
            continue
        wanted = spec["replicas"]
        if (health != "Healthy" or not state.get("ready") or not wanted or
                any(status.get(k, 0) != wanted for k in
                    ("replicas", "updatedReplicas", "readyReplicas", "availableReplicas"))):
            continue
        host = get(namespace, "route/weathernow")["spec"]["host"]
        code = run("curl", "--max-time", "10", "-sS", "-o", os.devnull, "-w", "%{http_code}", f"https://{host}/")
        if code == "200":
            return f'{pod["metadata"]["name"]} ready; {wanted}/{wanted} updated and available; route HTTP 200'
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("student", help="assigned Showroom username")
    parser.add_argument("app", choices=PATHS)
    parser.add_argument("mode", choices=("synced", "readiness-fault", "image-fault", "healthy"))
    parser.add_argument("--revision", help="full Gitea commit SHA (default: student main at start)")
    args = parser.parse_args()
    if args.app != "weathernow-lab" and args.mode != "synced":
        parser.error("WeatherNow workload checks require weathernow-lab")
    if not re.fullmatch(r"user-[a-z0-9-]+", args.student) or run("oc", "whoami") != args.student:
        raise RuntimeError(f"Sign in to the Showroom Terminal as {args.student} and run again.")
    ns = args.student + "-gitops"
    app = get(ns, "application.argoproj.io/" + args.app)
    source = app["spec"]["source"]
    route_items = get(args.student + "-demo", "routes")["items"]
    routes = {r["spec"]["host"] for r in route_items if r["spec"]["host"].startswith("gitea-" + args.student + "-demo.")}
    repos = {f"https://{host}/{args.student}/openshift-5-container-workspace{suffix}"
             for host in routes for suffix in ("", ".git")}
    if (source["repoURL"] not in repos or source.get("targetRevision") != "main"
            or source["path"] != PATHS[args.app] or app["spec"]["destination"].get("namespace") != ns
            or app["spec"]["destination"].get("server") != "https://kubernetes.default.svc"):
        raise RuntimeError("Check the Application source, branch, path and destination against the student guide.")
    revision = args.revision
    if revision is None:
        revision = run("git", "ls-remote", "--exit-code", source["repoURL"], "refs/heads/main").split()[0]
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise RuntimeError("Expected the full 40-character Gitea commit SHA.")
    print(f"Waiting up to 10 minutes for {args.app} in {ns} at {revision}", flush=True)
    deadline = time.monotonic() + 600
    last = ""
    while time.monotonic() < deadline:
        app = get(ns, "application.argoproj.io/" + args.app)
        state = app.get("status", {})
        sync = state.get("sync", {})
        health = state.get("health", {}).get("status", "Unknown")
        observed = f'{sync.get("revision", "pending")} {sync.get("status", "Unknown")} / {health}'
        if observed != last:
            print(observed, flush=True)
            last = observed
        if sync.get("status") == "Synced" and sync.get("revision") == revision:
            evidence = "matching Git revision" if args.mode == "synced" else weather_evidence(ns, args.mode, health)
            if evidence:
                print(f"PASS {revision} {evidence}")
                return
        time.sleep(5)
    raise RuntimeError(f"Timed out waiting for {args.mode} at {revision}. Last Argo observation: {last}\n"
                       f"To recheck this same commit: python3 check-release.py {args.student} "
                       f"{args.app} {args.mode} --revision {revision}")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, subprocess.TimeoutExpired, OSError) as exc:
        sys.exit(f"CHECK INCOMPLETE: {exc}")
