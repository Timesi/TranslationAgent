"""
定义流程中使用的状态
"""
from typing_extensions import TypedDict


class TranslationState(TypedDict):
    original_text: str          # 用户原始英文
    preprocessed_text: str      # 预处理后英文
    terminology_json: str       # 术语 JSON 字符串
    current_translation: str    # 当前轮次译文
    final_translation: str      # 最终定稿译文
    review_json: str            # 审阅意见 JSON
    review_comments: str        # 审阅意见文本
    iteration: int              # 已完成反思次数
    should_continue: bool       # 是否继续
    max_iterations: int         # 最大迭代次数