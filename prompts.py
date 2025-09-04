# 提示词模板
from langchain_core.prompts import ChatPromptTemplate

# 预处理节点
preprocess_node_prompt = ChatPromptTemplate.from_messages([
 ("system",
  "你是一名严谨的文本清理助手。\n"
  "任务及输出规则：\n"
  "1. 修正所有拼写和语法错误。\n"
  "2. 删除口语填充词：uh, um, ah 等。\n"
  "3. 仅删除不符合单词规律的连字符，保留合法的连字符；\n"
  "4. 去掉多余换行、空格，单词间只保留一个空格。\n"
  "5. 不做任何额外解释，仅返回清理后的完整英文文本。"),
 ("user", "{original_text}")
])

# 术语检查节点
terminology_node_prompt = ChatPromptTemplate.from_messages([
 ("system",
  "你是一名领域术语识别专家。\n"
  "任务：分析下列英文文本，判断其所属专业领域并尽可能提取关键术语。\n"
  "输出要求：\n"
  "1. 返回纯JSON，格式如下：\n"
  '{{\n'
  '  "domain": "<专业领域>",\n'
  '  "key_terms": [\n'
  '    {{"term": "<英文术语>", "explanation": "<中文解释>"}},\n'
  '    ...\n'
  '  ]\n'
  '}}\n'
  "2. 不要添加任何额外文字、注释或 Markdown 代码块标记。\n"
  "3. 必须保证 JSON 合法，可直接解析。"),
 ("user", "{preprocessed_text}")
])

# 翻译节点
translate_node_prompt = ChatPromptTemplate.from_messages([
 ("system",
  "你是资深{domain}领域英译中专家。\n"
  "任务：对【当前译文】进行终稿级润色。\n"
  "操作约束：\n"
  "1. 可任意增删字词、拆分或合并句子、调整语序，使中文自然、简洁、有节奏感；\n"
  "2. 必须严格沿用关键术语表（见下），严禁添加解释或括号注音；\n"
  "3. 禁止出现任何非译文字符（如“修改如下：”）。\n\n"
  "关键术语表：\n"
  "{terms}\n\n"
  "审阅意见：\n"
  "{review_comments}\n\n"
  "直接输出润色后的译文，无需任何额外说明。"),
 ("user", "{preprocessed_text}")
])

# 审查节点
review_node_prompt = ChatPromptTemplate.from_messages([
 ("system",
  "你是一名中文科技编辑，专门审校英译中的学术/技术译文。\n"
  "任务：对下方译文进行逐句审阅并提出改进建议，着重关注流畅性。\n"
  "审校维度：\n"
  "1. 流畅性：是否符合现代汉语表达语序和规则；\n"
  "2. 准确性：术语、数据、逻辑是否与原文一致；\n"
  "3. 精炼性：是否可删减冗余、合并重复；\n"
  "4. 风格一致性：整篇语气、格式是否统一。\n"
  "5. 逻辑性：是否符合中文的表述方式、语序。\n"
  "输出要求：\n"
  "1. 返回纯JSON，格式：\n"
  '  {{"comments": ["建议1", "建议2", ...], "continue": true/false}}\n'
  "2. 若仍有问题，continue=true；译文已完美则comments为''，continue=false。\n"
  "3. 禁止输出 JSON 以外的任何文字。"),
 ("user", "原文：\n{original_text}\n\n译文：\n{current_translation}")
])