import pytest
import os
from src.notion import NotionWrapper
from src.constants import (
    NOTION_PAGE_ID_ENV,
    TEST_PAGE_TITLE,
    NOTION_PARENT_BLOCK_ID,
    BlockType,
)
from notion_client.errors import APIResponseError
from notion_client import Client

@pytest.fixture(scope="module")
def notion():
    """Create a NotionWrapper instance for testing"""
    token = os.environ.get("NOTION_TOKEN")
    page_id = os.environ.get(NOTION_PAGE_ID_ENV)
    if not token or not page_id:
        pytest.skip("NOTION_TOKEN and NOTION_PAGE_ID environment variables must be set")
    return NotionWrapper()

@pytest.fixture(scope="module")
def test_page(notion):
    """Create a test page and clean it up after tests"""
    page = notion.client.pages.create(
        parent={"type": "page_id", "page_id": os.environ[NOTION_PAGE_ID_ENV]},
        properties={"title": {"title": [{"text": {"content": TEST_PAGE_TITLE}}]}}
    )
    yield page
    # Cleanup: Archive the test page
    notion.client.pages.update(page_id=page["id"], archived=True)

def test_get_page(notion, test_page):
    """Test retrieving a page"""
    result = notion.get_page(test_page["id"])
    assert result["id"] == test_page["id"]
    assert not result["archived"]

def test_add_page_with_parent(notion):
    """Test creating a new page with explicit parent"""
    new_page_title = "Test New Page Creation With Parent"
    result = notion.add_page(new_page_title, os.environ[NOTION_PAGE_ID_ENV])
    
    # Verify the page was created with correct title
    assert result["object"] == "page"
    assert not result["archived"]
    assert result["properties"]["title"]["title"][0]["text"]["content"] == new_page_title
    
    # Clean up: Archive the test page
    notion.client.pages.update(page_id=result["id"], archived=True)

def test_add_page_without_parent(notion):
    """Test creating a new page at root level"""
    new_page_title = "Test New Page Creation Root Level"
    result = notion.add_page(new_page_title)
    
    # Verify the page was created with correct title
    assert result["object"] == "page"
    assert not result["archived"]
    assert result["properties"]["title"]["title"][0]["text"]["content"] == new_page_title
    
    # Clean up: Archive the test page
    notion.client.pages.update(page_id=result["id"], archived=True)

def test_add_text(notion, test_page):
    """Test adding text to an existing page"""
    test_text = "Test content added to existing page ✨"
    result = notion.add_text(test_text, test_page["id"])
    
    # Verify the block was added
    assert result["object"] == "list"
    assert len(result["results"]) > 0
    
    last_block = result["results"][-1]
    assert last_block["type"] == "paragraph"
    assert last_block["paragraph"]["rich_text"][0]["text"]["content"] == test_text

def test_add_text_with_parent(notion):
    """Test adding text to an existing parent block"""
    test_text = "Test content added to parent block 🔗"
    result = notion.add_text(test_text, NOTION_PARENT_BLOCK_ID)
    
    # Verify the block was added to the correct parent
    assert result["object"] == "list"
    assert len(result["results"]) > 0
    last_block = result["results"][-1]
    assert last_block["type"] == "paragraph"
    assert last_block["paragraph"]["rich_text"][0]["text"]["content"] == test_text

def test_add_heading(notion, test_page):
    """Test adding a heading to an existing page"""
    test_text = "Test Heading"
    result = notion.add_text(test_text, test_page["id"], BlockType.HEADING_1)
    
    assert result["object"] == "list"
    assert len(result["results"]) > 0
    last_block = result["results"][-1]
    assert last_block["type"] == "heading_1"
    assert last_block["heading_1"]["rich_text"][0]["text"]["content"] == test_text

def test_add_code_block(notion, test_page):
    """Test adding a code block to an existing page"""
    test_code = "print('Hello, World!')"
    result = notion.add_code_block(test_code, test_page["id"], language="python")
    
    assert result["object"] == "list"
    assert len(result["results"]) > 0
    last_block = result["results"][-1]
    assert last_block["type"] == "code"
    assert last_block["code"]["rich_text"][0]["text"]["content"] == test_code
    assert last_block["code"]["language"] == "python"
