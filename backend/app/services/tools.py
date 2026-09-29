from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
@dataclass(frozen=True)
class Tool: name:str; handler:Callable[[dict[str,Any]],dict[str,Any]]
def lookup_asset(a:dict[str,Any])->dict[str,Any]: return {"status":"ok","asset":None,"query":a.get("query")}
def create_internal_note(a:dict[str,Any])->dict[str,Any]: return {"status":"created","content":a.get("content")}
def disable_user_access(a:dict[str,Any])->dict[str,Any]: return {"status":"simulated","reason":a.get("reason")}
TOOL_REGISTRY={t.name:t for t in (Tool("lookup_asset",lookup_asset),Tool("create_internal_note",create_internal_note),Tool("disable_user_access",disable_user_access))}
def execute_tool(name:str,arguments:dict[str,Any])->dict[str,Any]:
    tool=TOOL_REGISTRY.get(name)
    if tool is None: raise ValueError(f"Tool is not allow-listed: {name}")
    return tool.handler(arguments)
