"""
TLS Certificate Bundle Generator

Generates:
- CA cert/key pair
- Server cert/key pair signed by CA
- SSH key pair

Saves files in a structured output directory and writes a YAML config summary.
Configurable via CLI arguments and YAML input config.

Dependencies:
- OpenSSL must be installed and available on PATH
- ssh-keygen (from OpenSSH suite)
"""

import argparse
import subprocess
import time
import traceback
import socket
from pathlib import Path
import shutil
import re
import yaml

# ============================
# CONFIGURATION & CLI ARGUMENTS
# ============================

parser = argparse.ArgumentParser(
    description="Generate cert authentication pair and optionally upload to Vault."
)
parser.add_argument("--config_file", default=".yaml", help="Config file location")
parser.add_argument("--export_dir", default=Path("/").anchor, type=Path, help="Export directory for certificates")
parser.add_argument("--force", action="store_true", help="Force regeneration of certificates, even if they exist")
args = parser.parse_args()

# ============================
# LOAD YAML CONFIGURATION
# ============================

try:
    with open(args.config_file, "r") as f:
        config = yaml.safe_load(f)
except Exception as e:
    print(f"Error loading configuration file: {e}")
    exit(1)

try:
    CANAME = config["ca"]["name"]
    CN = config["ca"]["cn"]
    LABEL = config["ca"]["label"]
    ORGANIZATION = config["ca"]["organization"]
    COUNTRY = config["ca"]["country"]
    STATE = config["ca"]["state"]
except KeyError as e:
    print(f"Missing required configuration key: {e}")
    exit(1)

# ============================
# FORMATTERS
# ============================

def format_filename(org_str: str) -> str:
    formatted = re.sub(r'[^a-z\d]', '_', org_str.strip().lower())
    formatted = re.sub(r'_+', '_', formatted)
    return formatted

caname_prefix = format_filename(CANAME)
full_filename_prefix = f"{caname_prefix}"

# ============================
# FILE STRUCTURE SETUP
# ============================

export_dir = Path(args.export_dir) / full_filename_prefix
export_dir.mkdir(parents=True, exist_ok=True)

server_subfolder = export_dir / "server"
ca_subfolder = export_dir / "server/CAs"
ssh_subfolder = export_dir / "ssh"
for folder in [server_subfolder, ca_subfolder, ssh_subfolder]:
    folder.mkdir(parents=True, exist_ok=True)

try:
    SERVER_CN = config["server"]["cn"]
    SERVER_LABEL = config["server"]["label"]
except KeyError as e:
    print(f"Missing required server configuration key: {e}")
    exit(1)

# ============================
# PATHS
# ============================

ca_key_file = export_dir / f"ca_{full_filename_prefix}_private.key"
ca_cert_file = export_dir / f"ca_{full_filename_prefix}.crt"
server_key_file = export_dir / f"{full_filename_prefix}_private.key"
server_cert_file = export_dir / f"{full_filename_prefix}_public.crt"
ssh_key_file = ssh_subfolder / "id_rsa_ssh"

# ============================
# GENERATION
# ============================

if not ca_key_file.exists() or not ca_cert_file.exists() or args.force:
    print("\nGenerating CA private key and certificate...\n")
    subprocess.run(
        f'openssl ecparam -name prime256v1 -genkey -noout -out "{ca_key_file}"',
        shell=True, check=True
    )
    subprocess.run(
        f'openssl req -x509 -new -nodes -key "{ca_key_file}" '
        f'-sha256 -days 1826 -out "{ca_cert_file}" '
        f'-subj "/CN={CN}/C={COUNTRY}/ST={STATE}/L={LABEL}/O={ORGANIZATION}"',
        shell=True, check=True
    )
else:
    print("\nCA private key and certificate already exist. Skipping generation.\n")

if not server_key_file.exists() or not server_cert_file.exists() or args.force:
    print("\nGenerating server authentication key pair...\n")
    csr_file = export_dir / f"{SERVER_CN.replace('.', '_')}.csr"
    subprocess.run(
        f'openssl req -new -nodes -out "{csr_file}" '
        f'-newkey rsa:4096 -keyout "{server_key_file}" '
        f'-subj "/CN={SERVER_CN}/C={COUNTRY}/ST={STATE}/L={SERVER_LABEL}/O={ORGANIZATION}"',
        shell=True, check=True
    )
    subprocess.run(
        f'openssl x509 -req -in "{csr_file}" '
        f'-CA "{ca_cert_file}" -CAkey "{ca_key_file}" '
        f'-CAcreateserial -out "{server_cert_file}" -days 730 -sha256',
        shell=True, check=True
    )
else:
    print("\nServer private key and certificate already exist. Skipping generation.\n")

shutil.copy(server_key_file, server_subfolder / "private.key")
shutil.copy(server_cert_file, server_subfolder / "public.crt")
shutil.copy(ca_cert_file, ca_subfolder / "CA.crt")

if not ssh_key_file.exists() or args.force:
    print("\nGenerating SSH key pair...\n")
    subprocess.run(f'ssh-keygen -t rsa -b 4096 -f "{ssh_key_file}" -N ""', shell=True, check=True)
else:
    print("\nSSH key pair already exists. Skipping generation.\n")

# ============================
# OUTPUT METADATA
# ============================

output_config = {
    "metadata": {
        "profile_name": full_filename_prefix,
        "container_folder": str(export_dir),
        "export_dir": str(args.export_dir),
        "config_file": args.config_file,
        "force_regeneration": args.force,
    },
    "ca": config["ca"],
    "server": {"cn": SERVER_CN},
    "certificates": {
        "ca_cert": str(ca_cert_file),
        "server_cert": str(server_cert_file),
        "server_key": str(server_key_file),
        "ssh_key": str(ssh_key_file),
        "ssh_public_key": str(ssh_key_file) + ".pub",
    },
}

output_file = export_dir / f"{full_filename_prefix}.yaml"
with open(output_file, "w") as f:
    yaml.dump(output_config, f, default_flow_style=False)
print(f"\nOutput configuration file saved to: {output_file}")
