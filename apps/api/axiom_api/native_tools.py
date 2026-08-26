from axiom_core.tools import ToolCallResult, ToolDefinition, ToolRegistry

# CLAUDE.md §64's own demo: an in-memory mock "business record" store —
# deliberately not a real business system. The point is to prove the
# Policy Engine + Human Approval pipeline actually gates a real mutating
# call, not to model real business data.
_BUSINESS_RECORDS: dict[str, dict] = {}


def register_native_tools(registry: ToolRegistry) -> None:
    async def modify_business_record(arguments: dict) -> ToolCallResult:
        record_id = arguments["record_id"]
        fields = arguments.get("fields", {})
        _BUSINESS_RECORDS.setdefault(record_id, {}).update(fields)
        return ToolCallResult(content={"record_id": record_id, "record": _BUSINESS_RECORDS[record_id]})

    registry.register(
        ToolDefinition(
            name="modify_business_record",
            description="Create or update fields on a business record (demo — in-memory only).",
            input_schema={
                "type": "object",
                "properties": {
                    "record_id": {"type": "string"},
                    "fields": {"type": "object"},
                },
                "required": ["record_id"],
            },
            source="native",
            permissions=("business_record.write",),
            risk_level="high",
        ),
        modify_business_record,
    )
