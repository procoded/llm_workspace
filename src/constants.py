"""Constants used throughout the application."""
from enum import Enum

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING_1 = "heading_1"
    HEADING_2 = "heading_2"
    HEADING_3 = "heading_3"
    CODE = "code"
    QUOTE = "quote"
    BULLETED_LIST = "bulleted_list_item"
    NUMBERED_LIST = "numbered_list_item"

# Environment variable names
NOTION_PAGE_ID_ENV = "NOTION_PAGE_ID"

# Fixed IDs
NOTION_PARENT_BLOCK_ID = "15e8af5f-1697-8078-9272-e1ef84688ad8"
NOTION_PAGE_ID = "1568af5f1697808aba1cdc7c57f78ab3"

# Test data
TEST_PAGE_TITLE = "Test Page"
PARENT_TEST_PAGE_TITLE = "Parent Test Page"
