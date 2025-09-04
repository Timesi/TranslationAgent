# 智能体节点
import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from state import TranslationState
from typing import Dict, Any
from langchain_core.output_parsers import StrOutputParser
from prompts import preprocess_node_prompt, terminology_node_prompt, translate_node_prompt, review_node_prompt

load_dotenv()

# 模型
llm = ChatOpenAI(
    model="glm-4.5-flash",
    openai_api_key=os.getenv("ZAI_API_KEY"),
    openai_api_base="https://open.bigmodel.cn/api/paas/v4/"
)

# 预处理节点
def preprocess_node(state: TranslationState) -> Dict[str, Any]:
    print("=== 文本预处理 ===")
    print(f"输入文本: {state['original_text']}")
    corrected = (preprocess_node_prompt | llm | StrOutputParser()).invoke({"original_text": state["original_text"]})
    print(f"预处理后文本: {corrected}")
    print("=== 文本预处理结束 ===\n")
    return {"preprocessed_text": corrected}


# 术语检查节点
def terminology_node(state: TranslationState) -> Dict[str, Any]:
    print("=== 开始术语检查 ===")
    print(f"输入文本: {state['preprocessed_text']}")
    terminology_json = (terminology_node_prompt | llm | StrOutputParser()).invoke({"preprocessed_text": state["preprocessed_text"]})
    print(f"识别的领域和术语: {terminology_json}")
    print("=== 术语检查结束 ===\n")
    return {"terminology_json": terminology_json}


# 翻译节点
def translate_node(state: TranslationState) -> Dict[str, Any]:
    print("=== 开始翻译 ===")
    print(f"预处理文本: {state['preprocessed_text']}")
    term_data = json.loads(state["terminology_json"])
    terms_str = "\n".join(f"- {t['term']}: {t['explanation']}" for t in term_data["key_terms"])
    print(f"领域: {term_data['domain']}")
    print(f"术语表:\n{terms_str}")
    
    # 提取审阅意见
    review_comments = ""
    if state.get("review_json"):
        review_data = json.loads(state["review_json"])
        if "comments" in review_data:
            review_comments = "\n".join(f"- {comment}" for comment in review_data["comments"])
    if review_comments:
        print(f"审阅意见:\n{review_comments}")
    
    trans = (translate_node_prompt | llm | StrOutputParser()).invoke({
        "domain": term_data['domain'], 
        "terms": terms_str, 
        "preprocessed_text": state["preprocessed_text"],
        "review_comments": review_comments
    })
    print(f"翻译结果: {trans}")
    print("=== 翻译结束 ===\n")
    return {"current_translation": trans}


# 审阅节点
def review_node(state: TranslationState) -> Dict[str, Any]:
    print("=== 开始审阅 ===")
    print(f"原文: {state['original_text']}")
    print(f"当前译文: {state['current_translation']}")
    review_json = (review_node_prompt | llm | StrOutputParser()).invoke({"original_text": state["original_text"], "current_translation": state["current_translation"]})
    review = json.loads(review_json)
    print(f"审阅意见: {review_json}")
    print("=== 当前审阅结束 ===\n")
    
    # 提取审阅意见文本
    review_comments = ""
    if "comments" in review:
        review_comments = "\n".join(review["comments"])
    
    result = {
        "review_json": review_json,
        "review_comments": review_comments,
        "should_continue": review["continue"],
        "iteration": state["iteration"] + 1,
    }
    
    # 如果不再继续或达到最大迭代次数，则设置最终翻译
    if not review["continue"] or state["iteration"] + 1 >= state["max_iterations"]:
        result["final_translation"] = state["current_translation"]
    
    return result
