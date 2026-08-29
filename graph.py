import json
import datetime
from typing import TypedDict, Optional, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from models import AuditEntry

class GraphState(TypedDict):
    customer_id: str
    proposed_action: str
    confidence_score: float
    reasoning: str
    human_decision: Optional[str]
    final_action: Optional[str]

# Node 1: Agent Reasoning
def evaluate_customer(state: GraphState):
    customer_id = state.get("customer_id", "unknown")
    
    # Mocking LLM Reasoning to avoid needing API keys for this demo
    if customer_id == "CUST-001":
        proposed_action = "send_email"
        confidence_score = 0.90
        reasoning = "Khách hàng có dấu hiệu ít tương tác nhưng chưa nghiêm trọng. Đề xuất gửi email nhắc nhở."
    elif customer_id == "CUST-002":
        proposed_action = "increase_credit_limit"
        confidence_score = 0.99
        reasoning = "Khách hàng VIP, chi tiêu thường xuyên. Đề xuất tăng hạn mức tín dụng để tăng độ hài lòng."
    else:
        proposed_action = "send_email"
        confidence_score = 0.80
        reasoning = "Thiếu dữ liệu hành vi rõ ràng, độ tự tin thấp, gửi email thăm dò."
        
    return {
        "proposed_action": proposed_action,
        "confidence_score": confidence_score,
        "reasoning": reasoning
    }

# Conditional Routing
def route_action(state: GraphState) -> Literal["execute_high_risk_action", "execute_low_risk_action"]:
    action = state.get("proposed_action")
    confidence = state.get("confidence_score", 0.0)
    
    # Rule 1: Policy Override (Luôn review các hành động nhạy cảm)
    if action == "increase_credit_limit":
        return "execute_high_risk_action"
    
    # Rule 2: Auto-Execute (Low risk & High confidence)
    if confidence >= 0.85 and action == "send_email":
        return "execute_low_risk_action"
        
    # Rule 3: Escalate/Suggest (Low confidence)
    return "execute_high_risk_action"

# Audit Log Helper
def log_audit(entry: AuditEntry):
    log_file = "audit_log.json"
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            logs = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        logs = []
        
    logs.append(entry.model_dump())
    
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=4, ensure_ascii=False)

# Node: Auto Execute
def execute_low_risk_action(state: GraphState):
    action = state.get("proposed_action")
    print(f"Auto-executing: {action}")
    
    entry = AuditEntry(
        timestamp=datetime.datetime.now().isoformat(),
        agent_id="agent-01",
        action=action,
        confidence=state.get("confidence_score", 0.0),
        reviewer_id="system-auto",
        decision="Auto-Approve"
    )
    log_audit(entry)
    
    return {"final_action": action}

# Node: Execute with Human Decision
def execute_high_risk_action(state: GraphState):
    decision = state.get("human_decision")
    action = state.get("proposed_action")
    
    final_action = action
    
    if decision == "Approve":
        print(f"Executed approved action: {action}")
    elif decision == "Reject":
        print(f"Aborted action: {action}")
        final_action = "aborted"
    elif decision and decision.startswith("Edit:"):
        final_action = decision.replace("Edit:", "").strip()
        print(f"Executed edited action: {final_action}")
    
    entry = AuditEntry(
        timestamp=datetime.datetime.now().isoformat(),
        agent_id="agent-01",
        action=action,
        confidence=state.get("confidence_score", 0.0),
        reviewer_id="human-operator",
        decision=decision or "Unknown"
    )
    log_audit(entry)
    
    return {"final_action": final_action}

# Build and Compile Graph
builder = StateGraph(GraphState)

builder.add_node("evaluate_customer", evaluate_customer)
builder.add_node("execute_low_risk_action", execute_low_risk_action)
builder.add_node("execute_high_risk_action", execute_high_risk_action)

builder.add_edge(START, "evaluate_customer")
builder.add_conditional_edges("evaluate_customer", route_action)
builder.add_edge("execute_low_risk_action", END)
builder.add_edge("execute_high_risk_action", END)

memory = MemorySaver()
graph = builder.compile(
    checkpointer=memory,
    interrupt_before=["execute_high_risk_action"]
)
