"""IPv4 CIDR & VLSM subnet planner outputting Cisco wildcard masks for OSPF."""

from __future__ import annotations

import ipaddress
import math


def describe_cidr(cidr: str) -> dict:
    """Calculate network, broadcast, usable host range, and Cisco OSPF wildcard mask."""
    net = ipaddress.IPv4Network(cidr, strict=False)
    hosts = list(net.hosts())
    first_usable = str(hosts[0]) if hosts else str(net.network_address)
    last_usable = str(hosts[-1]) if hosts else str(net.broadcast_address)

    return {
        "cidr": str(net),
        "network": str(net.network_address),
        "netmask": str(net.netmask),
        "wildcard_mask": str(net.hostmask),
        "broadcast": str(net.broadcast_address),
        "first_usable": first_usable,
        "last_usable": last_usable,
        "usable_hosts": len(hosts),
    }


def allocate_vlsm_subnets(parent_cidr: str, host_requirements: list[dict]) -> list[dict]:
    """Allocate contiguous VLSM subnets ordered largest-requirement-first."""
    parent = ipaddress.IPv4Network(parent_cidr, strict=False)
    ordered = sorted(host_requirements, key=lambda item: int(item["hosts"]), reverse=True)

    allocations: list[dict] = []
    cursor = int(parent.network_address)
    parent_end = int(parent.broadcast_address)

    for req in ordered:
        needed_hosts = int(req["hosts"])
        if needed_hosts <= 0:
            raise ValueError("Host requirement must be positive.")
        total_addresses = needed_hosts + 2
        host_bits = math.ceil(math.log2(total_addresses))
        prefix = 32 - host_bits
        block_size = 1 << host_bits

        if cursor % block_size != 0:
            cursor = ((cursor // block_size) + 1) * block_size
        if cursor + block_size - 1 > parent_end:
            raise ValueError(f"Insufficient address space in {parent_cidr} for {req['name']}")

        subnet = ipaddress.IPv4Network((cursor, prefix))
        info = describe_cidr(str(subnet))
        allocations.append({"segment": req["name"], "requested_hosts": needed_hosts, **info})
        cursor += block_size

    return allocations
