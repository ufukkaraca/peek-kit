import os
import logging
from mcp.server.fastmcp import FastMCP
from peek_kit.tools.perception import register_perception_tools
from peek_kit.tools.action import register_action_tools
from peek_kit.tools.human import register_human_tools
from peek_kit.tools.output import register_output_tools
from peek_kit.utils.permissions import require_accessibility

# Setup basic logging
log_level_str = os.environ.get("PEEK_KIT_LOG_LEVEL", "INFO")
logging.basicConfig(level=getattr(logging, log_level_str))

def main():
    require_accessibility()

    mcp = FastMCP("peek-kit", dependencies=["pyobjc-framework-ApplicationServices", "Pillow", "atomacos", "jinja2"])

    register_perception_tools(mcp)
    register_action_tools(mcp)
    register_human_tools(mcp)
    register_output_tools(mcp)

    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
