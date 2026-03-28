"""自然语言意图识别规则。"""

from __future__ import annotations

CASE_HINTS = ["交互", "案例", "代码", "实现", "效果", "写进 KM"]
PROJECT_HINTS = ["项目", "版本", "阶段", "里程碑", "约束"]
PROFILE_HINTS = ["我", "偏好", "习惯", "画像", "常用"]


# 使用轻量关键字规则完成第一版意图识别，后续再考虑更复杂策略。
def classify_intent(text: str) -> str:
    """根据文本特征判断应写入的 KM 文档类型。

    参数:
        text (str): 用户输入的自然语言描述。

    返回:
        str: case / project / profile / inbox 之一。
    """
    if any(token in text for token in CASE_HINTS):
        return "case"
    if any(token in text for token in PROJECT_HINTS):
        return "project"
    if any(token in text for token in PROFILE_HINTS):
        return "profile"
    return "inbox"
