# NOEMA — Hetzner Cloud deployment plan

Status: prepared on an infrastructure branch; no server has been ordered and no cloud resources have been created.

## Purpose

Hetzner is the dedicated always-on host for NOEMA only. Do not deploy ASIX, RIDGE, or their databases or credentials here.

The host will run the existing single-host NOEMA service from `noema_core.service` under systemd. The current service provides a durable SQLite queue, allowlisted internal diagnostic handlers, workflow orchestration, interval scheduling, audit integrity checks, and graceful recovery. It does **not yet** implement external-source research connectors or autonomous scientific discovery. Those are separate application milestones and must not be represented as live merely because the host is online.

## Initial server profile

- Product: Hetzner Cloud shared AMD instance (initial staging/production host for the current single-host runtime)
- Suggested size: 8 vCPU, 16 GB RAM, 320 GB SSD/NVMe class (CPX42 where available; verify exact SKU and current price in Console)
- OS: Ubuntu 24.04 LTS
- Region: EU-central, initially Falkenstein (fsn1); compare measured latency from Georgia and the connected research/data services before finalizing. Helsinki (hel1) and Nuremberg (nbg1) are alternatives.
- Public networking: IPv4/IPv6 as required; no public application port is needed for the current worker-only runtime.
- Persistent state: `/var/lib/noema/noema-jobs.sqlite3`
- Process manager: systemd using the existing `deploy/systemd/noema.service`
- Runtime: Python 3.12 virtual environment; no Docker is required for the current service bootstrap.
- Backups: enable Hetzner daily server backups; separately export the SQLite database to independent storage and test restoration.

This is an initial capacity recommendation, not a performance guarantee. Benchmark actual NOEMA workloads before scaling or running large experiments continuously.

## Network and security baseline

1. Add an SSH public key in Hetzner Console before creating the server. Do not use password-based SSH.
2. Attach a Hetzner Firewall at creation.
3. Inbound: allow TCP/22 only from the operator's trusted source IP/CIDR where practical. Do not open 80/443/3000/5432/6379; the current service exposes no public HTTP API and uses local SQLite.
4. Outbound: allow DNS, NTP, HTTPS, and package/repository access needed for updates and explicitly approved public research sources.
5. Keep the host updated; enable unattended security updates.
6. Run the service as the dedicated unprivileged `noema` user. Keep `/var/lib/noema` owner-only; do not place API tokens or sensitive personal data in the current unencrypted SQLite queue.
7. Store future credentials in a root-readable environment file or secret manager, never in Git, command history, job payloads, or research artifacts.
8. Enable provider backups and maintain an independent off-host backup. A server backup does not replace application-level recovery tests.
9. Record deployment changes and service events; alert on service failure, disk pressure, backup failure, and repeated worker errors.

## Deployment procedure

After the server is created:

1. Connect using the injected SSH key and verify the host fingerprint.
2. Apply OS security updates; create the `noema` system account and `/opt/noema` code directory.
3. Install Python 3, venv support, Git, and CA certificates.
4. Clone `https://github.com/maisuradzee/bibmom.git` into `/opt/noema`.
5. Create `/opt/noema/.venv`.
6. Run the existing service preflight:
   `python -m noema_core.service --check --db /var/lib/noema/noema-jobs.sqlite3`
7. Install `deploy/systemd/noema.service`, reload systemd, enable and start it.
8. Verify `systemctl status noema`, `journalctl -u noema`, SQLite integrity, and successful self-check workflow runs.
9. Reboot the host and verify the service returns automatically.
10. Restore a backup into a disposable test environment and verify the database integrity before declaring recovery ready.

Detailed baseline commands are maintained in [SERVICE_DEPLOYMENT.md](SERVICE_DEPLOYMENT.md).

## Release and rollback

- Deploy only from a reviewed, tested Git commit; record the exact commit SHA in the deployment log.
- Do not deploy directly from an unreviewed research branch.
- Keep the previous known-good release available for rollback.
- Stop the service before filesystem-level SQLite restore; never copy a live WAL database as if it were a single static file.
- A failed health check blocks promotion and publication.

## Research and publication boundaries

The server may autonomously run only registered, reviewed handlers. Unknown task types remain blocked. Public-source retrieval must respect source terms, access controls, licensing, privacy, and retention rules. Internal research drafts can be generated automatically; final publication, sensitive-data processing, financial transactions, legal commitments, destructive operations, and permission changes remain review-gated according to `noema_core/mission.json`.

## Acceptance checklist

- [ ] Server created in selected EU-central location with SSH key
- [ ] Firewall attached; only restricted SSH inbound
- [ ] Ubuntu security updates applied
- [ ] Dedicated `noema` user and owner-only state directory
- [ ] Existing service preflight passes
- [ ] systemd service starts and survives reboot
- [ ] SQLite integrity and audit-chain checks pass
- [ ] Daily provider backup enabled
- [ ] Independent off-host backup and restore test pass
- [ ] Logs and resource monitoring configured
- [ ] Actual research connectors separately implemented, reviewed, and tested before claiming autonomous research capability

## Cost control

No server, backup add-on, volume, or paid resource is created by this plan. Confirm the exact monthly cap, hourly price, IPv4 charge, backup charge, and tax shown in Hetzner Console before ordering. Delete unused cloud resources to stop ongoing billing.
