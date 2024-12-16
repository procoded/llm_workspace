import os
from typing import Optional
from notion_client import Client
from src.constants import NOTION_PAGE_ID_ENV, BlockType

class NotionWrapper:
    """Wrapper class for Notion API interactions."""
    
    def __init__(self):
        """Initialize the Notion client using environment token."""
        self.client = Client(auth=os.environ["NOTION_TOKEN"])
    
    def get_page(self, page_id: str) -> dict:
        """
        Retrieve a Notion page by its ID.
        
        Args:
            page_id (str): The ID of the Notion page to retrieve
            
        Returns:
            dict: The page data returned from the Notion API
            
        Raises:
            Exception: If NOTION_TOKEN environment variable is not set
            APIResponseError: If the API request fails
        """
        return self.client.pages.retrieve(page_id)

    def add_page(self, title: str, parent_page_id: Optional[str] = None) -> dict:
        """
        Create a new Notion page with the given title.
        
        Args:
            title (str): The title for the new page
            parent_page_id (str, optional): The ID of the parent page to create the new page under.
                                          If None, uses the default page ID from NOTION_PAGE_ID_ENV.
            
        Returns:
            dict: The newly created page data from the Notion API
            
        Raises:
            Exception: If NOTION_TOKEN environment variable is not set
            APIResponseError: If the API request fails
        """
        if parent_page_id is None:
            parent_page_id = os.environ[NOTION_PAGE_ID_ENV]
            
        parent = {"type": "page_id", "page_id": parent_page_id}
            
        return self.client.pages.create(
            parent=parent,
            properties={"title": {"title": [{"text": {"content": title}}]}}
        )
    
    def add_text(
        self, 
        text: str, 
        parent_block: str,
        block_type: BlockType = BlockType.PARAGRAPH
    ) -> dict:
        """
        Add a text block to an existing Notion page or block.
        
        Args:
            text (str): The text content to add
            parent_block (str): ID of the parent page or block to add text to
            block_type (BlockType): The type of block to create (paragraph, heading, etc.)
                
        Returns:
            dict: The response from the Notion API
            
        Raises:
            Exception: If NOTION_TOKEN environment variable is not set
            APIResponseError: If the API request fails
        """
        block_content = {
            "object": "block",
            "type": block_type.value,
        }
        
        # Handle different block types
        if block_type in [BlockType.HEADING_1, BlockType.HEADING_2, BlockType.HEADING_3]:
            block_content[block_type.value] = {
                "rich_text": [{"type": "text", "text": {"content": text}}]
            }
        else:
            block_content[block_type.value] = {
                "rich_text": [{"type": "text", "text": {"content": text}}]
            }

        return self.client.blocks.children.append(
            block_id=parent_block,
            children=[block_content]
        )

    def add_code_block(
        self, 
        code: str, 
        parent_block: str,
        language: str = "plain text"
    ) -> dict:
        """
        Add a code block to an existing Notion page or block.
        
        Args:
            code (str): The code content to add
            parent_block (str): ID of the parent page or block to add code to
            language (str): Programming language for syntax highlighting
                
        Returns:
            dict: The response from the Notion API
            
        Raises:
            Exception: If NOTION_TOKEN environment variable is not set
            APIResponseError: If the API request fails
        """
        return self.client.blocks.children.append(
            block_id=parent_block,
            children=[{
                "object": "block",
                "type": "code",
                "code": {
                    "rich_text": [{"type": "text", "text": {"content": code}}],
                    "language": language
                }
            }]
        )
