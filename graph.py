"""
英文→中文反思翻译 Agent
"""
from state import TranslationState
from langgraph.graph import StateGraph, END
from nodes import preprocess_node, terminology_node, translate_node, review_node


# 定义条件边
def route_after_review(state: TranslationState) -> str:
    if state["should_continue"] and state["iteration"] < state["max_iterations"]:
        print("决策: 继续翻译迭代")
        return "translate"
    print("决策: 结束翻译流程")
    return END


# 构建langgraph图
workflow = StateGraph(TranslationState)
workflow.add_node("preprocess", preprocess_node)
workflow.add_node("terminology", terminology_node)
workflow.add_node("translate", translate_node)
workflow.add_node("review", review_node)

workflow.set_entry_point("preprocess")
workflow.add_edge("preprocess", "terminology")
workflow.add_edge("terminology", "translate")
workflow.add_edge("translate", "review")
workflow.add_conditional_edges("review", route_after_review)

app = workflow.compile()

# 运行
if __name__ == "__main__":
    input_text = (
        "QuantumScape unveiled its 7nm ASIC-based neural processing unit (NPU) integrating 128 fault-tolerant qubits, achieving quantum-classical hybrid computing breakthroughs.  The chip uses Grover’s algorithm for weight optimization, slashing neural network training time via MPI-driven parallel processing.  Its topological qubit array enables for quantum error correction and neuro-symbolic inference engine reduces latency by 40% in drug molecular simulations.  \"This merges ASIC efficiency with quantum parallelism,\" noted CEO Dr. Lai, marking a post-Moore’s Law milestone in exascale AI acceleration."
    )

    initial: TranslationState = {
        "original_text": input_text,
        "preprocessed_text": "",
        "terminology_json": "",
        "current_translation": "",
        "final_translation": "",
        "review_json": "",
        "review_comments": "",
        "iteration": 0,
        "should_continue": True,
        "max_iterations": 2,
    }

    print("开始翻译流程")
    print(f"用户输入: {input_text}\n")
    result = app.invoke(initial)
    print("=== 最终译文 ===")
    print(result["final_translation"])