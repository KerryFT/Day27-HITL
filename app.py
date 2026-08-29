import streamlit as st
from graph import graph

st.set_page_config(page_title="HITL Approval", layout="wide")
st.title("Human-in-the-Loop Approval System")

if "thread_id" not in st.session_state:
    st.session_state.thread_id = "thread-1"

with st.sidebar:
    st.header("Graph Controls")
    thread_id = st.text_input("Thread ID", value=st.session_state.thread_id)
    st.session_state.thread_id = thread_id
    
    customer_id = st.selectbox(
        "Select Mock Customer", 
        ["CUST-001 (High confidence, low risk)", 
         "CUST-002 (High risk override)", 
         "CUST-003 (Low confidence escalation)"]
    )
    cust_id_clean = customer_id.split()[0]
    
    if st.button("Start Workflow", type="primary"):
        config = {"configurable": {"thread_id": st.session_state.thread_id}}
        initial_state = {"customer_id": cust_id_clean}
        
        st.write("Invoking graph...")
        for event in graph.stream(initial_state, config):
            pass # just run until interrupt or end
        st.rerun()

config = {"configurable": {"thread_id": st.session_state.thread_id}}
current_state = graph.get_state(config)

if current_state and current_state.next:
    st.warning("⚠️ Workflow is pending human review!", icon="⚠️")
    
    state_vals = current_state.values
    st.subheader("Agent Reasoning Data")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**Customer ID:** {state_vals.get('customer_id')}")
        st.info(f"**Proposed Action:** {state_vals.get('proposed_action')}")
    with col2:
        st.info(f"**Confidence Score:** {state_vals.get('confidence_score')}")
        st.info(f"**Reasoning:** {state_vals.get('reasoning')}")
        
    st.divider()
    st.subheader("Human Action Required")
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        if st.button("✅ Approve", use_container_width=True):
            graph.update_state(config, {"human_decision": "Approve"})
            for _ in graph.stream(None, config): pass
            st.success("Approved!")
            st.rerun()
            
    with c2:
        if st.button("❌ Reject", use_container_width=True):
            graph.update_state(config, {"human_decision": "Reject"})
            for _ in graph.stream(None, config): pass
            st.error("Rejected!")
            st.rerun()
            
    with c3:
        edited_action = st.text_input("Edit proposed action", value=state_vals.get("proposed_action"))
        if st.button("📝 Edit & Submit", use_container_width=True):
            graph.update_state(config, {"human_decision": f"Edit: {edited_action}"})
            for _ in graph.stream(None, config): pass
            st.success(f"Edited and submitted!")
            st.rerun()

elif current_state and not current_state.next and "final_action" in current_state.values:
    st.success("Workflow completed.")
    st.write(f"**Final Executed Action:** {current_state.values.get('final_action')}")
    
    if current_state.values.get("human_decision"):
        st.write(f"**Human Decision recorded:** {current_state.values.get('human_decision')}")
    else:
        st.write("**Auto-Executed by Policy**")
else:
    st.info("No active workflow for this thread. Start one from the sidebar.")
