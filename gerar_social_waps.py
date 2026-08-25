#!/usr/bin/env python3
"""Gera uma lista DNSBL social sem WhatsApp e Google Ads."""

from __future__ import annotations

import argparse
import ipaddress
import re
import sys
import tempfile
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


SOURCE_URL = (
    "https://raw.githubusercontent.com/StevenBlack/hosts/"
    "master/alternates/social/hosts"
)

# O domínio-base e todos os seus subdomínios são liberados.
ALLOW_SUFFIXES = (
    "whatsapp.com",
    "whatsapp.net",
    "wa.me",
    "googleadservices.com",
)

# Somente estes nomes exatos são liberados; outros subdomínios google.com
# continuam seguindo a lista original.
ALLOW_EXACT = {
    "ads.google.com",
    "adservice.google.com",
}

HOSTNAME_RE = re.compile(
    r"^(?=.{1,253}\.?$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"
    r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.?$",
    re.IGNORECASE,
)


def is_allowed(domain: str) -> bool:
    """Retorna True quando o domínio deve ser removido da DNSBL."""
    if domain in ALLOW_EXACT:
        return True
    return any(domain == suffix or domain.endswith("." + suffix) for suffix in ALLOW_SUFFIXES)


def extract_domains(content: str) -> tuple[set[str], int]:
    """Extrai, normaliza e filtra domínios de um arquivo hosts."""
    domains: set[str] = set()
    removed = 0

    for raw_line in content.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue

        fields = line.split()
        if len(fields) >= 2:
            try:
                ipaddress.ip_address(fields[0])
            except ValueError:
                candidates = fields
            else:
                candidates = fields[1:]
        else:
            candidates = fields

        for candidate in candidates:
            domain = candidate.lower().rstrip(".")
            if domain == "localhost" or not HOSTNAME_RE.fullmatch(domain):
                continue
            if is_allowed(domain):
                removed += 1
            else:
                domains.add(domain)

    return domains, removed


def download(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "social-waps-generator/1.0"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read().decode("utf-8-sig")


def render(domains: set[str], removed: int, source_url: str) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    header = [
        "# social-waps.txt - DNSBL social sem WhatsApp e Google Ads",
        f"# Fonte: {source_url}",
        f"# Gerado em: {timestamp}",
        f"# Dominios bloqueados: {len(domains)}",
        f"# Entradas liberadas pelo filtro: {removed}",
        "# Formato: hosts (compativel com pfBlockerNG DNSBL)",
        "",
    ]
    return "\n".join(header + [f"0.0.0.0 {domain}" for domain in sorted(domains)]) + "\n"


def write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="\n", delete=False, dir=path.parent
    ) as temporary:
        temporary.write(content)
        temporary_path = Path(temporary.name)
    temporary_path.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path(__file__).with_name("social-waps.txt"),
        help="arquivo de saida (padrao: ao lado do script)",
    )
    parser.add_argument("--source", default=SOURCE_URL, help="URL da lista de origem")
    args = parser.parse_args()

    try:
        source = download(args.source)
        domains, removed = extract_domains(source)
        if not domains:
            raise RuntimeError("a fonte nao retornou dominios validos")
        write_atomic(args.output, render(domains, removed, args.source))
    except Exception as error:
        print(f"Erro: {error}", file=sys.stderr)
        return 1

    print(
        f"OK: {args.output} ({len(domains)} dominios; "
        f"{removed} entradas liberadas)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
