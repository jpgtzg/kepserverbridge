"""
Written by Juan Pablo Gutierrez

Helper script to dump the details of an OPC UA node.
"""

from asyncua.common.node import Node
from asyncua import ua
from dotenv import load_dotenv
from typing import Any, Awaitable, Callable, Optional

load_dotenv()

async def dump_node_details(node: Node, indent: int = 0) -> None:
    pad = "  " * indent

    async def try_await(label: str, fn: Callable[[], Awaitable[Any]]) -> Optional[Any]:
        try:
            v = await fn()
        except Exception as e:
            print(f"{pad}- {label}: <error {type(e).__name__}: {e}>")
            return None
        print(f"{pad}- {label}: {await _safe_repr(v)}")
        return v

    print(f"{pad}=== OPC UA node dump ===")
    print(f"{pad}- nodeid: {await _safe_repr(node.nodeid)}")
    try:
        print(f"{pad}- nodeid_str: {node.nodeid.to_string()}")
    except Exception as e:
        print(f"{pad}- nodeid_str: <error {type(e).__name__}: {e}>")

    # High-level "nice" helpers
    await try_await("browse_name", node.read_browse_name)
    await try_await("display_name", node.read_display_name)
    await try_await("description", node.read_description)
    await try_await("node_class", node.read_node_class)
    await try_await("data_type (NodeId)", node.read_data_type)
    await try_await("data_type_as_variant_type", node.read_data_type_as_variant_type)
    await try_await("value_rank", node.read_value_rank)
    await try_await("array_dimensions", node.read_array_dimensions)
    await try_await("access_level", node.get_access_level)
    await try_await("user_access_level", node.get_user_access_level)
    await try_await("event_notifier", node.read_event_notifier)
    await try_await("data_type_definition", node.read_data_type_definition)

    # Value in multiple shapes (python value + DataValue with timestamps/status/variant)
    await try_await("value (python)", node.read_value)
    dv = await try_await("value (DataValue)", lambda: node.read_data_value(raise_on_bad_status=False))
    if dv is not None:
        try:
            print(f"{pad}- datavalue.StatusCode: {await _safe_repr(dv.StatusCode)}")
            print(f"{pad}- datavalue.SourceTimestamp: {await _safe_repr(dv.SourceTimestamp)}")
            print(f"{pad}- datavalue.ServerTimestamp: {await _safe_repr(dv.ServerTimestamp)}")
            print(f"{pad}- datavalue.SourcePicoseconds: {await _safe_repr(dv.SourcePicoseconds)}")
            print(f"{pad}- datavalue.ServerPicoseconds: {await _safe_repr(dv.ServerPicoseconds)}")
            print(f"{pad}- datavalue.Value: {await _safe_repr(dv.Value)}")
            if dv.Value is not None:
                try:
                    print(f"{pad}- datavalue.Value.VariantType: {await _safe_repr(dv.Value.VariantType)}")
                except Exception as e:
                    print(f"{pad}- datavalue.Value.VariantType: <error {type(e).__name__}: {e}>")
                try:
                    print(f"{pad}- datavalue.Value.Value: {await _safe_repr(dv.Value.Value)}")
                except Exception as e:
                    print(f"{pad}- datavalue.Value.Value: <error {type(e).__name__}: {e}>")
        except Exception as e:
            print(f"{pad}- datavalue details: <error {type(e).__name__}: {e}>")

    # Brute-force: attempt to read every OPC UA AttributeId and print StatusCode + Value
    # This is often the fastest way to discover what a server actually supports on a given node.
    print(f"{pad}--- attribute sweep (AttributeIds) ---")
    for attr in ua.AttributeIds:
        try:
            adv = await node.read_attribute(attr, raise_on_bad_status=False)
            # adv.Value is a Variant or None
            val_repr = "<None>" if adv.Value is None else await _safe_repr(adv.Value)
            print(f"{pad}- {attr.name} ({int(attr)}): Status={await _safe_repr(adv.StatusCode)}, Value={val_repr}")
        except Exception as e:
            print(f"{pad}- {attr.name} ({int(attr)}): <error {type(e).__name__}: {e}>")



async def _safe_repr(v: Any, max_len: int = 800) -> str:
    """
    Best-effort repr that won't explode your terminal on huge arrays/bytes.
    """
    try:
        s = repr(v)
    except Exception as e:
        s = f"<repr failed: {type(e).__name__}: {e}>"
    if len(s) > max_len:
        return s[:max_len] + f"... <truncated, {len(s)} chars>"
    return s

