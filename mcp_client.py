# mcp_client.py  – v2
from composio_openai import ComposioToolSet, App
toolset = ComposioToolSet()
entity  = toolset.get_entity(id="sarthakgupta8305@gmail.com")

# GOOGLEDRIVE_GOOGLE_DRIVE_CHANGES needs an *empty* config dict
response = entity.enable_trigger(
    app          = App.GOOGLEDRIVE,
    trigger_name = "GOOGLEDRIVE_GOOGLE_DRIVE_CHANGES",
    config       = {}                  # ← keep empty for the global feed
)
print("Trigger status:", response["status"])

