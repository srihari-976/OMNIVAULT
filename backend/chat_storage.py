"""
Chat Storage Module
Handles persistent storage of chat conversations as JSON files
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional
import traceback

class ChatStorage:
    """Manages chat persistence using file-based JSON storage"""
    
    def __init__(self, storage_dir: str = "./chat_history"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
    
    def _get_chat_filepath(self, chat_id: str) -> str:
        """Get filepath for a chat ID"""
        return os.path.join(self.storage_dir, f"chat_{chat_id}.json")
    
    def save_chat(self, chat_id: str, chat_data: Dict) -> bool:
        """
        Save or update a chat to disk
        
        Args:
            chat_id: Unique chat identifier
            chat_data: Chat data including messages, title, etc.
            
        Returns:
            True if successful, False otherwise
        """
        try:
            filepath = self._get_chat_filepath(chat_id)
            
            # Add timestamps
            if 'created_at' not in chat_data:
                chat_data['created_at'] = datetime.now().isoformat()
            chat_data['updated_at'] = datetime.now().isoformat()
            chat_data['id'] = chat_id
            
            # Write to file with pretty formatting
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(chat_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving chat {chat_id}: {str(e)}")
            traceback.print_exc()
            return False
    
    def load_chat(self, chat_id: str) -> Optional[Dict]:
        """
        Load a specific chat from disk
        
        Args:
            chat_id: Chat identifier
            
        Returns:
            Chat data dict or None if not found
        """
        try:
            filepath = self._get_chat_filepath(chat_id)
            
            if not os.path.exists(filepath):
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                chat_data = json.load(f)
            
            return chat_data
            
        except Exception as e:
            print(f"❌ Error loading chat {chat_id}: {str(e)}")
            traceback.print_exc()
            return None
    
    def delete_chat(self, chat_id: str) -> bool:
        """
        Delete a chat from disk
        
        Args:
            chat_id: Chat identifier
            
        Returns:
            True if deleted, False if not found or error
        """
        try:
            filepath = self._get_chat_filepath(chat_id)
            
            if not os.path.exists(filepath):
                return False
            
            os.remove(filepath)
            print(f"✓ Deleted chat: {chat_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error deleting chat {chat_id}: {str(e)}")
            traceback.print_exc()
            return False
    
    def get_chat_list(self) -> List[Dict]:
        """
        Get list of all chats with metadata
        
        Returns:
            List of chat metadata dicts (id, title, created_at, updated_at)
        """
        try:
            chats = []
            
            # List all chat files
            if not os.path.exists(self.storage_dir):
                return []
            
            for filename in os.listdir(self.storage_dir):
                if filename.startswith("chat_") and filename.endswith(".json"):
                    try:
                        filepath = os.path.join(self.storage_dir, filename)
                        with open(filepath, 'r', encoding='utf-8') as f:
                            chat_data = json.load(f)
                        
                        # Extract metadata
                        chats.append({
                            'id': chat_data.get('id'),
                            'title': chat_data.get('title', 'Untitled Chat'),
                            'created_at': chat_data.get('created_at'),
                            'updated_at': chat_data.get('updated_at'),
                            'message_count': len(chat_data.get('messages', []))
                        })
                    except Exception as e:
                        print(f"⚠️ Error reading chat file {filename}: {str(e)}")
                        continue
            
            # Sort by updated_at (most recent first)
            chats.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
            
            return chats
            
        except Exception as e:
            print(f"❌ Error getting chat list: {str(e)}")
            traceback.print_exc()
            return []
    
    def load_all_chats(self) -> List[Dict]:
        """
        Load all complete chats from disk
        
        Returns:
            List of complete chat data dicts
        """
        try:
            chats = []
            
            # List all chat files
            if not os.path.exists(self.storage_dir):
                return []
            
            for filename in os.listdir(self.storage_dir):
                if filename.startswith("chat_") and filename.endswith(".json"):
                    try:
                        filepath = os.path.join(self.storage_dir, filename)
                        with open(filepath, 'r', encoding='utf-8') as f:
                            chat_data = json.load(f)
                        chats.append(chat_data)
                    except Exception as e:
                        print(f"⚠️ Error reading chat file {filename}: {str(e)}")
                        continue
            
            # Sort by updated_at (most recent first)
            chats.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
            
            return chats
            
        except Exception as e:
            print(f"❌ Error loading all chats: {str(e)}")
            traceback.print_exc()
            return []
