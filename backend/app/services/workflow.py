from __future__ import annotations

from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from app.schemas import AgentDecision
from app.services.agent import AgentProvider, get_agent_provider
from app.services.policy import evaluate_policy
from app.services.tools import execute_tool


class WorkflowState(TypedDict, total=False):
    title: str
    description: str
    decision: dict
    requires_approval: bool
    policy_reason: str
    tool_result: dict


def build_workflow(provider: AgentProvider | None = None):
    active_provider = provider or get_agent_provider()

    def decide(state: WorkflowState) -> WorkflowState:
        decision = active_provider.decide(state["title"], state["description"])
        return {"decision": decision.model_dump(mode="json")}

    def apply_policy(state: WorkflowState) -> WorkflowState:
        decision = AgentDecision.model_validate(state["decision"])
        result = evaluate_policy(decision)
        return {
            "requires_approval": result.requires_approval,
            "policy_reason": result.reason,
        }

    def route_after_policy(state: WorkflowState) -> Literal["execute_tool", "await_approval"]:
        return "await_approval" if state["requires_approval"] else "execute_tool"

    def execute(state: WorkflowState) -> WorkflowState:
        decision = AgentDecision.model_validate(state["decision"])
        result = execute_tool(decision.proposed_tool, decision.tool_arguments)
        return {"tool_result": result}

    def await_approval(_: WorkflowState) -> WorkflowState:
        return {}

    graph = StateGraph(WorkflowState)
    graph.add_node("decide", decide)
    graph.add_node("apply_policy", apply_policy)
    graph.add_node("execute_tool", execute)
    graph.add_node("await_approval", await_approval)
    graph.add_edge(START, "decide")
    graph.add_edge("decide", "apply_policy")
    graph.add_conditional_edges(
        "apply_policy",
        route_after_policy,
        {
            "execute_tool": "execute_tool",
            "await_approval": "await_approval",
        },
    )
    graph.add_edge("execute_tool", END)
    graph.add_edge("await_approval", END)
    return graph.compile()


def run_workflow(title: str, description: str, provider: AgentProvider | None = None) -> WorkflowState:
    workflow = build_workflow(provider)
    result = workflow.invoke({"title": title, "description": description})
    return WorkflowState(**result)
