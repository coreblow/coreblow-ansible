#!/usr/bin/env python3
import os
import sys
import yaml
import re

print("=== Validating CoreBlow Ansible Role & Playbook ===")

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# 1. Validate YAML syntax for all role files
yaml_files = [
    "playbook.yml",
    "inventory-sample.yml",
    "requirements.yml",
    "roles/coreblow_host/defaults/main.yml",
    "roles/coreblow_host/handlers/main.yml",
    "roles/coreblow_host/tasks/main.yml",
]

for rel_path in yaml_files:
    full_path = os.path.join(repo_root, rel_path)
    if not os.path.exists(full_path):
        print(f"FAIL: Missing expected file {rel_path}")
        sys.exit(1)
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        print(f"✓ Validated YAML: {rel_path}")
    except Exception as e:
        print(f"FAIL: YAML syntax error in {rel_path}: {e}")
        sys.exit(1)

# 2. Check defaults
defaults_path = os.path.join(repo_root, "roles/coreblow_host/defaults/main.yml")
with open(defaults_path, "r", encoding="utf-8") as f:
    defaults = yaml.safe_load(f)

assert defaults.get("coreblow_gateway_port") == 18789, f"coreblow_gateway_port must be 18789, got {defaults.get('coreblow_gateway_port')}"
assert defaults.get("coreblow_version") == "2.1.2", f"coreblow_version must be 2.1.2, got {defaults.get('coreblow_version')}"
assert defaults.get("coreblow_node_major_version") == 22, "coreblow_node_major_version must be 22"
print("✓ Role defaults verified (port 18789, version 2.1.2, Node 22).")

# 3. Check tasks content
tasks_path = os.path.join(repo_root, "roles/coreblow_host/tasks/main.yml")
with open(tasks_path, "r", encoding="utf-8") as f:
    tasks_content = f.read()

assert "ansible.builtin.group" in tasks_content, "Must ensure system group exists"
assert "ansible.builtin.user" in tasks_content, "Must ensure dedicated service user exists"
assert "0700" in tasks_content, "Must enforce 0700 permissions on ~/.coreblow directory"
assert "NoNewPrivileges" not in tasks_content, "Hardening directives should live in the systemd template"
assert "ansible.builtin.template" in tasks_content, "Must deploy systemd unit from template"
assert "ansible.builtin.uri" in tasks_content, "Must include Gateway healthcheck"
print("✓ Tasks verified (service user, 0700 permissions, systemd template, healthcheck).")

# 4. Check systemd unit template
tmpl_path = os.path.join(repo_root, "roles/coreblow_host/templates/coreblow.service.j2")
with open(tmpl_path, "r", encoding="utf-8") as f:
    tmpl = f.read()

assert "NoNewPrivileges=yes" in tmpl, "Must enforce NoNewPrivileges=yes in systemd unit"
assert "ProtectSystem=strict" in tmpl, "Must enforce ProtectSystem=strict in systemd unit"
assert "ProtectHome=read-only" in tmpl, "Must enforce ProtectHome=read-only in systemd unit"
assert "PrivateTmp=yes" in tmpl, "Must enforce PrivateTmp=yes in systemd unit"
assert "18789" in tmpl or "{{ coreblow_gateway_port }}" in tmpl, "Must configure gateway port in systemd unit"
print("✓ Hardened systemd unit template verified (NoNewPrivileges, ProtectSystem=strict, PrivateTmp).")

# 5. Check brand sovereignty & path hygiene across all text files
for root, _, files in os.walk(repo_root):
    if ".git" in root:
        continue
    for file in files:
        if file.endswith((".yml", ".yaml", ".j2", ".md", ".cfg")):
            fpath = os.path.join(root, file)
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                c = f.read()
            if re.search(r"/Users/|/home/(?!node|coreblow)", c):
                print(f"FAIL: Hardcoded local home path in {os.path.relpath(fpath, repo_root)}")
                sys.exit(1)
            if re.search(r"\b(openclaw|clawhub)\b", c, re.IGNORECASE):
                print(f"FAIL: Brand leak in {os.path.relpath(fpath, repo_root)}")
                sys.exit(1)

print("✓ Brand sovereignty and path hygiene verified.")
print("✅ All CoreBlow Ansible checks passed successfully.")
