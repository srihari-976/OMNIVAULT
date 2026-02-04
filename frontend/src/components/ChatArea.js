import React, { useState, useRef, useEffect } from 'react';
import './ChatArea.css';
import { useTheme } from '../context/ThemeContext';
import ThinkingIndicator from './ThinkingIndicator';
import CodeBlock from './CodeBlock';

const ChatArea = ({ messages, onSendMessage, sidebarOpen, onToggleSidebar, isThinking, onNewChat }) => {
  const { theme, toggleTheme } = useTheme();
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showPlusMenu, setShowPlusMenu] = useState(false);
  const [activeMode, setActiveMode] = useState(null); // 'summarize', 'deep-research', or null
  const [uploadedFiles, setUploadedFiles] = useState([]); // Track uploaded files
  const [isUploading, setIsUploading] = useState(false);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);
  const plusMenuRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [input]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (plusMenuRef.current && !plusMenuRef.current.contains(event.target)) {
        setShowPlusMenu(false);
      }
    };

    if (showPlusMenu) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showPlusMenu]);

  const handlePlusMenuAction = (action) => {
    if (isThinking || isLoading) return;
    setShowPlusMenu(false);
    // Handle different actions
    switch (action) {
      case 'deep-research':
        setActiveMode('deep-research');
        break;
      case 'add-files':
        // Trigger file input
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.multiple = true;
        fileInput.accept = '.pdf,.doc,.docx,.txt,.md,.py,.js,.java,.cpp,.c,.html,.css,.json,.xml';
        fileInput.onchange = async (e) => {
          const files = Array.from(e.target.files);
          if (files.length > 0) {
            setIsUploading(true);

            // Upload each file individually
            for (const file of files) {
              try {
                const formData = new FormData();
                formData.append('file', file);

                const uploadResponse = await fetch('/api/upload', {
                  method: 'POST',
                  body: formData,
                });

                if (!uploadResponse.ok) {
                  const errorData = await uploadResponse.json().catch(() => ({}));
                  throw new Error(errorData.error || `Upload failed: ${uploadResponse.status}`);
                }

                const uploadData = await uploadResponse.json();

                // Add file to uploaded files list with processing status
                const newFile = {
                  id: uploadData.file_id,
                  name: uploadData.filename || file.name,
                  status: 'queued',
                  progress: 10,
                  uploadedAt: new Date().toISOString()
                };

                setUploadedFiles(prev => [...prev, newFile]);

                // Start polling for status
                pollFileStatus(uploadData.file_id);

              } catch (error) {
                console.error(`Error uploading ${file.name}:`, error);
                alert(`Failed to upload ${file.name}: ${error.message}`);
              }
            }

            setIsUploading(false);
          }
        };
        fileInput.click();
        break;
      case 'summarize':
        setActiveMode('summarize');
        break;
      default:
        break;
    }
  };

  const removeActiveMode = () => {
    setActiveMode(null);
  };

  const removeFile = (fileId) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const pollFileStatus = async (fileId) => {
    const maxAttempts = 60; // Poll for up to 1 minute
    let attempts = 0;

    const poll = async () => {
      try {
        const response = await fetch(`/api/upload/status/${fileId}`);
        if (!response.ok) {
          throw new Error('Failed to get status');
        }

        const status = await response.json();

        // Update file in list
        setUploadedFiles(prev => prev.map(f => {
          if (f.id === fileId) {
            return {
              ...f,
              status: status.status,
              progress: status.progress || 0,
              message: status.message,
              chunks: status.chunks_added,
              wordCount: status.word_count,
              fileType: status.file_type
            };
          }
          return f;
        }));

        // Continue polling if not completed or failed
        if (status.status !== 'completed' && status.status !== 'failed' && attempts < maxAttempts) {
          attempts++;
          setTimeout(poll, 1000); // Poll every second
        }
      } catch (error) {
        console.error('Error polling file status:', error);
        // Retry on error
        if (attempts < maxAttempts) {
          attempts++;
          setTimeout(poll, 2000); // Retry after 2 seconds on error
        }
      }
    };

    poll();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading || isThinking) return;

    let message = input.trim();
    let mode = 'chat';

    // Prepend instruction based on active mode
    if (activeMode === 'summarize') {
      message = `${message}, do summarize this`;
      mode = 'summarize';
      setActiveMode(null); // Clear mode after sending
    } else if (activeMode === 'deep-research') {
      message = `${message}, do deep research on this`;
      mode = 'deep-research';
      setActiveMode(null); // Clear mode after sending
    }

    setInput('');
    setIsLoading(true);

    await onSendMessage(message, mode);
    setIsLoading(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  // Parse message content to detect and render code blocks
  const parseMessage = (content) => {
    const codeBlockRegex = /```(\w+)?\n?([\s\S]*?)```/g;
    const parts = [];
    let lastIndex = 0;
    let match;

    while ((match = codeBlockRegex.exec(content)) !== null) {
      // Add text before code block
      if (match.index > lastIndex) {
        const text = content.substring(lastIndex, match.index);
        if (text.trim()) {
          parts.push({ type: 'text', content: text });
        }
      }

      // Add code block
      const language = match[1] || '';
      const code = match[2].trim();
      if (code) {
        parts.push({ type: 'code', language, code });
      }

      lastIndex = match.index + match[0].length;
    }

    // Add remaining text
    if (lastIndex < content.length) {
      const text = content.substring(lastIndex);
      if (text.trim()) {
        parts.push({ type: 'text', content: text });
      }
    }

    // If no code blocks found, return original content as text
    if (parts.length === 0) {
      return [{ type: 'text', content }];
    }

    return parts;
  };

  return (
    <div className="chat-area">
      <div className="chat-header">
        <div className="header-left">
          <h1 className="chat-title">OMNIVAULT</h1>
        </div>
        <div className="header-right">
          <button className="theme-toggle" onClick={toggleTheme} title={theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme'}>
            {theme === 'dark' ? (
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="5" stroke="currentColor" strokeWidth="2" />
                <path d="M12 1V3M12 21V23M4.22 4.22L5.64 5.64M18.36 18.36L19.78 19.78M1 12H3M21 12H23M4.22 19.78L5.64 18.36M18.36 5.64L19.78 4.22" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              </svg>
            ) : (
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            )}
          </button>
          <a
            href="https://github.com/srihari-976/OMNIVAULT"
            target="_blank"
            rel="noopener noreferrer"
            className="github-button"
            title="View on GitHub"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2C6.477 2 2 6.477 2 12c0 4.42 2.865 8.17 6.839 9.49.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.603-3.369-1.34-3.369-1.34-.454-1.156-1.11-1.463-1.11-1.463-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.578 9.578 0 0112 6.836c.85.004 1.705.114 2.504.336 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.203 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C19.138 20.167 22 16.418 22 12c0-5.523-4.477-10-10-10z" />
            </svg>
          </a>
        </div>
      </div>

      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="welcome-screen">
            <div className="welcome-content">
              <h2>OMNIVAULT</h2>
              <div className="suggestions">
                <div className="suggestion-card">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    <path d="M2 17L12 22L22 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    <path d="M2 12L12 17L22 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                  <div>
                    <h3>Examples</h3>
                    <p>"Explain quantum computing in simple terms"</p>
                  </div>
                </div>
                <div className="suggestion-card">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    <path d="M2 17L12 22L22 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    <path d="M2 12L12 17L22 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                  <div>
                    <h3>Capabilities</h3>
                    <p>"Remembers what user said earlier in the conversation"</p>
                  </div>
                </div>
                <div className="suggestion-card">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    <path d="M2 17L12 22L22 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    <path d="M2 12L12 17L22 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                  <div>
                    <h3>Limitations</h3>
                    <p>"May occasionally generate incorrect information"</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="messages">
            {messages.map((message) => (
              <div key={message.id} className={`message ${message.role}`}>
                <div className="message-avatar">
                  {message.role === 'user' ? (
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                      <circle cx="12" cy="7" r="4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  ) : (
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                      <path d="M2 17L12 22L22 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                      <path d="M2 12L12 17L22 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  )}
                </div>
                <div className="message-content">
                  {parseMessage(message.content).map((part, index) => {
                    if (part.type === 'code') {
                      return <CodeBlock key={index} code={part.code} language={part.language} />;
                    }
                    return (
                      <div key={index} className="message-text">
                        {part.content.split('\n').map((line, lineIndex, array) => (
                          <React.Fragment key={lineIndex}>
                            {line}
                            {lineIndex < array.length - 1 && <br />}
                          </React.Fragment>
                        ))}
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
            {isThinking && (
              <div className="message assistant">
                <div className="message-avatar">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    <path d="M2 17L12 22L22 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    <path d="M2 12L12 17L22 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                </div>
                <div className="message-content">
                  <ThinkingIndicator />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      <div className="input-container">
        <form onSubmit={handleSubmit} className="input-form">
          {activeMode && (
            <div className="mode-chip-container">
              <div className="mode-chip">
                <span className="mode-chip-text">
                  {activeMode === 'summarize' ? 'Summarize' : 'Deep Research'}
                </span>
                <button
                  type="button"
                  className="mode-chip-close"
                  onClick={removeActiveMode}
                  title="Remove mode"
                >
                  <svg width="14" height="14" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M4 4L12 12M12 4L4 12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                  </svg>
                </button>
              </div>
            </div>
          )}
          {uploadedFiles.length > 0 && (
            <div className="file-chips-container">
              {uploadedFiles.map(file => (
                <div key={file.id} className={`file-chip ${file.status || ''}`}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M13 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V9L13 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    <path d="M13 2V9H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                  <span className="file-chip-name">
                    {file.name}
                    {file.status && file.status !== 'completed' && (
                      <span className="file-chip-status">
                        {file.status === 'queued' && ' (Queued)'}
                        {file.status === 'processing' && ' (Processing...)'}
                        {file.status === 'indexing' && ' (Indexing...)'}
                        {file.status === 'failed' && ' (Failed)'}
                      </span>
                    )}
                    {file.status === 'completed' && file.chunks && (
                      <span className="file-chip-status"> ({file.chunks} chunks)</span>
                    )}
                  </span>
                  <button
                    type="button"
                    className="file-chip-close"
                    onClick={() => removeFile(file.id)}
                    title="Remove file"
                  >
                    <svg width="14" height="14" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M4 4L12 12M12 4L4 12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                    </svg>
                  </button>
                </div>
              ))}
            </div>
          )}
          {isUploading && (
            <div className="upload-status">
              <span>Uploading files...</span>
            </div>
          )}
          <div className="input-wrapper">
            <div className="plus-button-wrapper" ref={plusMenuRef}>
              <button
                type="button"
                className="plus-button"
                onClick={() => setShowPlusMenu(!showPlusMenu)}
                title="More options"
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 5V19M5 12H19" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                </svg>
              </button>
              {showPlusMenu && (
                <div className="plus-menu">
                  <button
                    type="button"
                    className="plus-menu-item"
                    onClick={() => handlePlusMenuAction('deep-research')}
                  >
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <circle cx="11" cy="11" r="8" stroke="currentColor" strokeWidth="2" />
                      <path d="M21 21L16.65 16.65" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                    </svg>
                    <span>Deep Research</span>
                  </button>
                  <button
                    type="button"
                    className="plus-menu-item"
                    onClick={() => handlePlusMenuAction('add-files')}
                  >
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                      <path d="M7 10L12 15L17 10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                      <path d="M12 15V3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                    <span>Add Photos and Files</span>
                  </button>
                  <button
                    type="button"
                    className="plus-menu-item"
                    onClick={() => handlePlusMenuAction('summarize')}
                  >
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M4 19.5C4 18.837 4.26339 18.2011 4.73223 17.7322C5.20107 17.2634 5.83696 17 6.5 17H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                      <path d="M6.5 2H20V22H6.5C5.83696 22 5.20107 21.7366 4.73223 21.2678C4.26339 20.7989 4 20.163 4 19.5V4.5C4 3.83696 4.26339 3.20107 4.73223 2.73223C5.20107 2.26339 5.83696 2 6.5 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                    <span>Summarize</span>
                  </button>
                </div>
              )}
            </div>
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Message OMNIVAULT..."
              className="chat-input"
              rows="1"
              disabled={isLoading || isThinking}
            />
            <button
              type="submit"
              className="send-button"
              disabled={!input.trim() || isLoading || isThinking}
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M1.5 1.5L14.5 8L1.5 14.5M1.5 1.5L6.5 8L1.5 14.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </button>
          </div>
        </form>
        <div className="input-footer">
          <p>OMNIVAULT can make mistakes. Check important info.</p>
        </div>
      </div>
    </div>
  );
};

export default ChatArea;

