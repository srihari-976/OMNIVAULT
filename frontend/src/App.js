import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import Settings from './components/Settings';
import { useTheme } from './context/ThemeContext';

function App() {
  const { theme } = useTheme();
  const [chats, setChats] = useState([]);
  const [currentChatId, setCurrentChatId] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [isThinking, setIsThinking] = useState(false);
  const [chatsLoaded, setChatsLoaded] = useState(false);
  const saveTimeoutRef = useRef(null);

  // Load chats from backend on startup
  const loadChatsFromBackend = async () => {
    try {
      const response = await fetch('/api/chats');
      if (response.ok) {
        const data = await response.json();
        const loadedChats = data.chats || [];

        // Convert to frontend format
        const formattedChats = loadedChats.map(chat => ({
          id: parseInt(chat.id) || chat.id,
          title: chat.title,
          messages: [] // Will load when selected
        }));

        setChats(formattedChats);
        setChatsLoaded(true);
        console.log(`✓ Loaded ${formattedChats.length} chats from backend`);
      }
    } catch (error) {
      console.error('Error loading chats:', error);
      setChatsLoaded(true);
    }
  };

  // Save chat to backend (debounced)
  const saveChatToBackend = async (chatId, chatMessages, chatTitle) => {
    try {
      await fetch('/api/chats/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id: chatId.toString(),
          title: chatTitle || 'New Chat',
          messages: chatMessages || []
        })
      });
      console.log('✓ Chat saved to backend');
    } catch (error) {
      console.error('Error saving chat:', error);
    }
  };

  const createNewChat = () => {
    const newChat = {
      id: Date.now(),
      title: 'New Chat',
      messages: []
    };
    setChats([newChat, ...chats]);
    setCurrentChatId(newChat.id);
    setMessages([]);
  };

  const selectChat = async (chatId) => {
    setCurrentChatId(chatId);

    // Try to load from backend first
    try {
      const response = await fetch(`/api/chats/${chatId}`);
      if (response.ok) {
        const chatData = await response.json();
        setMessages(chatData.messages || []);
        return;
      }
    } catch (error) {
      console.error('Error loading chat from backend:', error);
    }

    // Fallback to local state
    const chat = chats.find(c => c.id === chatId);
    if (chat) {
      setMessages(chat.messages || []);
    }
  };

  const deleteChat = async (chatId) => {
    // Delete from backend
    try {
      await fetch(`/api/chats/${chatId}`, { method: 'DELETE' });
    } catch (error) {
      console.error('Error deleting chat from backend:', error);
    }

    // Delete from local state
    setChats(chats.filter(c => c.id !== chatId));
    if (currentChatId === chatId) {
      setCurrentChatId(null);
      setMessages([]);
    }
  };

  const updateChatTitle = (chatId, title) => {
    setChats(chats.map(c => c.id === chatId ? { ...c, title } : c));
  };

  const extractTitleFromMessage = (message) => {
    // Common question words and stop words to exclude
    const stopWords = ['why', 'what', 'who', 'when', 'where', 'how', 'is', 'are', 'was', 'were', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as', 'can', 'could', 'should', 'would', 'will', 'this', 'that', 'these', 'those'];

    // Remove punctuation and convert to lowercase
    let cleaned = message.replace(/[^\w\s]/g, ' ').toLowerCase().trim();

    // Split into words
    let words = cleaned.split(/\s+/);

    // Filter out stop words and short words (less than 3 characters)
    words = words.filter(word =>
      word.length >= 3 &&
      !stopWords.includes(word)
    );

    // Take first 4-5 meaningful words
    const titleWords = words.slice(0, 5);

    if (titleWords.length === 0) {
      // If no meaningful words, use first 30 characters
      return message.substring(0, 30).trim();
    }

    // Capitalize first letter of first word
    const title = titleWords.join(' ');
    return title.charAt(0).toUpperCase() + title.slice(1);
  };

  const addMessage = async (userMessage, mode = 'chat', attachedFiles = []) => {
    setIsThinking(true);
    const newUserMessage = {
      role: 'user',
      content: userMessage,
      id: Date.now(),
      files: attachedFiles.length > 0 ? attachedFiles : undefined
    };

    const updatedMessages = [...messages, newUserMessage];
    setMessages(updatedMessages);

    let updatedChats = chats;
    if (currentChatId) {
      const chat = chats.find(c => c.id === currentChatId);
      let newTitle = chat.title;

      // Auto-rename if it's a new chat (has default title) and has no messages yet
      // This ensures we only rename on the first message
      if ((chat.title === 'New Chat' || !chat.messages || chat.messages.length === 0) && userMessage.length > 0) {
        newTitle = extractTitleFromMessage(userMessage);
      }

      updatedChats = chats.map(c =>
        c.id === currentChatId
          ? { ...c, messages: updatedMessages, title: newTitle }
          : c
      );
      setChats(updatedChats);
    }

    try {
      // Map frontend modes to backend modes
      let backendMode = mode;
      let useRag = true;

      if (mode === 'rag-enhanced') {
        backendMode = 'chat';
        useRag = true;
      } else if (mode === 'summarize') {
        backendMode = 'summarize';
        useRag = false;
      } else if (mode === 'deep-research') {
        backendMode = 'deep-research';
        useRag = true;
      } else {
        backendMode = 'chat';
        useRag = true;
      }

      // Build conversation history for context
      const conversationHistory = messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }));

      let response;
      let data;

      // Use dedicated endpoint for deep-research (has web search)
      if (mode === 'deep-research') {
        response = await fetch('/api/deep-research', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            query: userMessage
          }),
        });
      } else {
        response = await fetch('/api/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message: userMessage,
            mode: backendMode,
            use_rag: useRag,
            conversation_history: conversationHistory
          }),
        });
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `Server error: ${response.status}`);
      }

      data = await response.json();

      // Handle different response formats
      let responseText = data.response || data.summary || data.research || '';

      if (!responseText) {
        throw new Error('No response received from server');
      }

      const assistantMessage = {
        role: 'assistant',
        content: responseText,
        id: Date.now() + 1
      };

      const finalMessages = [...updatedMessages, assistantMessage];
      setMessages(finalMessages);

      if (currentChatId) {
        // Find the current chat to get the updated title
        const currentChat = updatedChats.find(c => c.id === currentChatId);
        const chatTitle = currentChat?.title || 'New Chat';

        // Use updatedChats to preserve the title that was just set
        const newChats = updatedChats.map(c =>
          c.id === currentChatId
            ? { ...c, messages: finalMessages }
            : c
        );
        setChats(newChats);

        // Save to backend immediately with messages
        saveChatToBackend(currentChatId, finalMessages, chatTitle);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        role: 'assistant',
        content: `Error: ${error.message}. Please make sure the backend server is running on port 5000.`,
        id: Date.now() + 1
      };
      const finalMessages = [...updatedMessages, errorMessage];
      setMessages(finalMessages);

      if (currentChatId) {
        // Find the current chat to get the updated title
        const currentChat = updatedChats.find(c => c.id === currentChatId);
        const chatTitle = currentChat?.title || 'New Chat';

        // Use updatedChats to preserve the title that was just set
        const newChats = updatedChats.map(c =>
          c.id === currentChatId
            ? { ...c, messages: finalMessages }
            : c
        );
        setChats(newChats);

        // Save to backend immediately with messages
        saveChatToBackend(currentChatId, finalMessages, chatTitle);
      }
    } finally {
      setIsThinking(false);
    }
  };

  // Load chats on mount
  useEffect(() => {
    loadChatsFromBackend();
  }, []);

  // Create new chat if no chats exist after loading
  useEffect(() => {
    if (chatsLoaded && chats.length === 0) {
      createNewChat();
    }
  }, [chatsLoaded, chats.length]);

  // Auto-save current chat when messages change (debounced)
  useEffect(() => {
    if (!currentChatId || messages.length === 0 || !chatsLoaded) return;

    // Clear previous timeout
    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current);
    }

    // Set new timeout for debounced save
    saveTimeoutRef.current = setTimeout(() => {
      // Find the current chat's title
      const currentChat = chats.find(c => c.id === currentChatId);
      const chatTitle = currentChat?.title || 'New Chat';

      // Update local chats state
      setChats(prevChats =>
        prevChats.map(c =>
          c.id === currentChatId
            ? { ...c, messages }
            : c
        )
      );

      // Save to backend with current data
      saveChatToBackend(currentChatId, messages, chatTitle);
    }, 500); // 500ms debounce

    return () => {
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current);
      }
    };
  }, [messages, currentChatId, chatsLoaded, chats]);

  return (
    <div className={`app theme-${theme}`}>
      <Sidebar
        chats={chats}
        currentChatId={currentChatId}
        onSelectChat={selectChat}
        onNewChat={createNewChat}
        onDeleteChat={deleteChat}
        onRenameChat={updateChatTitle}
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        onSettings={() => setSettingsOpen(true)}
      />
      <ChatArea
        messages={messages}
        onSendMessage={addMessage}
        sidebarOpen={sidebarOpen}
        onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
        isThinking={isThinking}
        onNewChat={createNewChat}
      />
      {settingsOpen && (
        <Settings onClose={() => setSettingsOpen(false)} />
      )}
    </div>
  );
}

export default App;

