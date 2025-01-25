import os
import json
import requests
from typing import List, Dict
import logging
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LinkWardenManager:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('LINKWARDEN_API_KEY')
        
        # Use environment variables with default values
        self.base_url = os.getenv('LINKWARDEN_BASE_URL', 'http://localhost:3002/api/v1')
        self.ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        
        # New environment variable to skip links with existing tags
        self.skip_tagged_links = os.getenv('SKIP_LINKS_WITH_TAGS', 'false').lower() in ['true', '1', 'yes']
        
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    
    def get_ollama_tags(self, text: str, approved_tags: List[str]) -> List[str]:
        """Get tag suggestions from Ollama and match with approved tags."""
        # Check if text is empty or too short
        if not text or len(text.strip()) < 10:
            logger.warning(f"Text too short for tag suggestion: '{text}'")
            return []

        try:
            # Construct a more detailed prompt
            prompt = f"""
You are an expert at extracting relevant tags from content. 
Analyze the following text and suggest tags from this approved list: {', '.join(approved_tags)}

Guidelines:
- Only suggest tags that are EXACTLY in the approved list
- Be precise and selective
- Return tags as a comma-separated list
- Minimum 1 tag, Maximum 5 tags

Text to analyze (len: {len(text)}):
{text[:500]}...

Suggested Tags:"""
            
            # Log the full prompt being sent
            logger.debug(f"Full Ollama Prompt:\n{prompt}")
            
            # Prepare the request payload
            payload = {
                "model": "phi3:mini-4k",
                "prompt": prompt,
                "stream": False,
                "temperature": 0.1,
                "num_predict": 50,
            }
            
            # Send request to Ollama
            response = requests.post(
                f'{self.ollama_url}/api/generate',
                json=payload,
                timeout=10
            )
            
            # Check response status
            if response.status_code != 200:
                logger.error(f"Ollama returned non-200 status code: {response.status_code}")
                logger.error(f"Response content: {response.text}")
                return []
            
            # Parse the response
            try:
                result = response.json()
            except ValueError:
                logger.error(f"Failed to parse JSON response: {response.text}")
                return []
            
            # Extract and process response
            if 'response' in result:
                response_text = result['response'].lower().strip()
                logger.debug(f"Raw Ollama response: {response_text}")
                
                # Parse tags
                suggested = [tag.strip() for tag in response_text.split(',')]
                suggested_tags = [tag for tag in suggested if tag in approved_tags]
                
                logger.debug(f"Filtered tags: {suggested_tags}")
                
                return suggested_tags[:5]
            
            logger.warning("No response key found in Ollama result")
            return []
            
        except requests.exceptions.RequestException as req_error:
            logger.error(f"Network error getting Ollama tags: {req_error}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error getting Ollama tags: {e}", exc_info=True)
            return []

    def load_approved_tags(self, tags_file: str) -> List[str]:
        try:
            with open(tags_file, 'r') as f:
                # Log each tag being loaded
                tags = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                logger.debug(f"Loaded tags: {tags}")
                return tags
        except FileNotFoundError:
            logger.error(f"Tags file {tags_file} not found")
            return []

    def get_all_links(self) -> List[Dict]:
        try:
            response = requests.get(f'{self.base_url}/links', headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            # Log details about the links
            logger.debug(f"Total links retrieved: {len(data.get('response', []))}")
            for link in data.get('response', []):
                logger.debug(f"Link details - Name: {link.get('name')}, URL: {link.get('url')}")
            
            return data.get('response', [])
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching links: {str(e)}")
            return []

    def update_link_tags(self, link_id: int, link_data: Dict, new_tags: List[str]) -> bool:
        try:
            update_data = {
                "id": link_id,
                "name": link_data.get('name', ''),
                "url": link_data.get('url', ''),
                "description": link_data.get('description', ''),
                "tags": [{"name": tag} for tag in new_tags],
                "collection": link_data.get('collection', {"id": 0})
            }
            
            # Log the update details
            logger.debug(f"Updating link {link_id} with tags: {new_tags}")
            logger.debug(f"Full update payload: {json.dumps(update_data, indent=2)}")
            
            response = requests.put(
                f'{self.base_url}/links/{link_id}',
                headers=self.headers,
                json=update_data
            )
            response.raise_for_status()
            logger.info(f"Successfully updated tags for link {link_id}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Error updating link {link_id}: {e}")
            return False

def main():
    manager = LinkWardenManager()
    
    # Load approved tags
    approved_tags = manager.load_approved_tags('tags.txt')
    logger.info(f"Loaded {len(approved_tags)} approved tags")
    
    # Get all links
    links = manager.get_all_links()
    logger.info(f"Found {len(links)} links")
    
    # Process each link
    for link in links:
        name = link.get('name', '')
        description = link.get('description', '')
        text_content = link.get('textContent', '')
        url = link.get('url', '')
        existing_tags = link.get('tags', [])
        
        # Check if we should skip links with existing tags
        if manager.skip_tagged_links and existing_tags:
            logger.info(f"Skipping '{name}' - already has {len(existing_tags)} tags")
            continue
        
        # Combine text for analysis, prioritizing content
        text_to_analyze = text_content or description or name
        
        logger.debug(f"Analyzing link: {name}")
        logger.debug(f"Text length for tag suggestion: {len(text_to_analyze)}")
        
        # Get tag suggestions from Ollama
        suggested_tags = manager.get_ollama_tags(text_to_analyze, approved_tags)
        
        if suggested_tags:
            success = manager.update_link_tags(
                link_id=link['id'],
                link_data=link,
                new_tags=suggested_tags
            )
            if success:
                logger.info(f"Updated tags for '{name}': {suggested_tags}")
            else:
                logger.error(f"Failed to update tags for '{name}'")
        else:
            logger.warning(f"No tags suggested for '{name}'")

if __name__ == "__main__":
    main()
