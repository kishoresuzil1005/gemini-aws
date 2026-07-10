from tests.utils.builders import build_tool_result

PUBLIC_RDS = build_tool_result(
    tool_name="SecurityTool",
    context={"severity": "CRITICAL", "exposure": "PUBLIC", "issue": "RDS is public"}
)

PRIVATE_RDS = build_tool_result(
    tool_name="InventoryTool",
    context={"severity": "INFO", "exposure": "PRIVATE", "issue": "RDS is private"}
)

HIGH_PRIVATE = build_tool_result(
    tool_name="SecurityTool",
    context={"severity": "HIGH", "exposure": "PRIVATE", "issue": "Private high risk"}
)

LOW_PUBLIC = build_tool_result(
    tool_name="SecurityTool",
    context={"severity": "LOW", "exposure": "PUBLIC", "issue": "Public low risk"}
)

INFO_ISOLATED = build_tool_result(
    tool_name="InventoryTool",
    context={"severity": "INFO", "exposure": "ISOLATED", "issue": "Isolated info"}
)
