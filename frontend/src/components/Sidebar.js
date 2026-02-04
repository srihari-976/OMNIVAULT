import React, { useState, useRef, useEffect } from 'react';
import './Sidebar.css';

const Sidebar = ({ chats, currentChatId, onSelectChat, onNewChat, onDeleteChat, onRenameChat, isOpen, onToggle, onSettings }) => {
  const [hoveredChat, setHoveredChat] = useState(null);
  const [showMenuFor, setShowMenuFor] = useState(null);
  const [editingChatId, setEditingChatId] = useState(null);
  const [editValue, setEditValue] = useState('');
  const menuRef = useRef(null);
  const editInputRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setShowMenuFor(null);
      }
    };

    if (showMenuFor) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showMenuFor]);

  useEffect(() => {
    if (editingChatId && editInputRef.current) {
      editInputRef.current.focus();
      editInputRef.current.select();
    }
  }, [editingChatId]);

  const handleMenuClick = (e, chatId) => {
    e.stopPropagation();
    setShowMenuFor(showMenuFor === chatId ? null : chatId);
  };

  const handleRename = (chatId) => {
    const chat = chats.find(c => c.id === chatId);
    if (chat) {
      setEditValue(chat.title);
      setEditingChatId(chatId);
      setShowMenuFor(null);
    }
  };

  const handleRenameSubmit = (chatId) => {
    if (editValue.trim()) {
      onRenameChat(chatId, editValue.trim());
    }
    setEditingChatId(null);
    setEditValue('');
  };

  const handleRenameCancel = () => {
    setEditingChatId(null);
    setEditValue('');
  };

  const handleRenameKeyDown = (e, chatId) => {
    if (e.key === 'Enter') {
      handleRenameSubmit(chatId);
    } else if (e.key === 'Escape') {
      handleRenameCancel();
    }
  };

  // Always show a small sidebar with icons
  return (
    <>
      <div className={`sidebar ${isOpen ? 'sidebar-expanded' : 'sidebar-collapsed'}`}>
        {isOpen ? (
          <>
            <div className="sidebar-header">
              <button className="new-chat-btn" onClick={onNewChat}>
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M8 3V13M3 8H13" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                </svg>
                New chat
              </button>
              <button className="sidebar-toggle" onClick={onToggle} title="Collapse sidebar">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M15 18L9 12L15 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </button>
            </div>
            <div className="sidebar-chats">
              {chats.map(chat => (
                <div
                  key={chat.id}
                  className={`chat-item ${currentChatId === chat.id ? 'active' : ''}`}
                  onMouseEnter={() => setHoveredChat(chat.id)}
                  onMouseLeave={() => {
                    setHoveredChat(null);
                    if (showMenuFor !== chat.id) {
                      setShowMenuFor(null);
                    }
                  }}
                  onClick={() => {
                    if (!editingChatId) {
                      onSelectChat(chat.id);
                    }
                  }}
                >
                  <div className="chat-item-content">
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M2 3H14M2 8H14M2 13H14" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                    </svg>
                    {editingChatId === chat.id ? (
                      <input
                        ref={editInputRef}
                        className="chat-title-input"
                        value={editValue}
                        onChange={(e) => setEditValue(e.target.value)}
                        onBlur={() => handleRenameSubmit(chat.id)}
                        onKeyDown={(e) => handleRenameKeyDown(e, chat.id)}
                        onClick={(e) => e.stopPropagation()}
                      />
                    ) : (
                      <span className="chat-title">{chat.title}</span>
                    )}
                  </div>
                  {hoveredChat === chat.id && !editingChatId && (
                    <div className="chat-item-actions" ref={menuRef}>
                      <button
                        className="chat-menu-btn"
                        onClick={(e) => handleMenuClick(e, chat.id)}
                        title="More options"
                      >
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <circle cx="8" cy="4" r="1.5" fill="currentColor" />
                          <circle cx="8" cy="8" r="1.5" fill="currentColor" />
                          <circle cx="8" cy="12" r="1.5" fill="currentColor" />
                        </svg>
                      </button>
                      {showMenuFor === chat.id && (
                        <div className="chat-menu">
                          <button
                            className="chat-menu-item"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleRename(chat.id);
                            }}
                          >
                            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                              <path d="M11.3333 2.00001C11.5084 1.8249 11.7163 1.68604 11.9446 1.59129C12.1729 1.49654 12.4171 1.44775 12.6667 1.44775C12.9162 1.44775 13.1604 1.49654 13.3887 1.59129C13.617 1.68604 13.8249 1.8249 14 2.00001C14.1751 2.17512 14.314 2.38305 14.4087 2.61132C14.5035 2.83959 14.5523 3.08381 14.5523 3.33334C14.5523 3.58287 14.5035 3.82709 14.4087 4.05536C14.314 4.28363 14.1751 4.49156 14 4.66668L5.00001 13.6667L1.33334 14.6667L2.33334 11L11.3333 2.00001Z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                            </svg>
                            <span>Rename</span>
                          </button>
                          <button
                            className="chat-menu-item"
                            onClick={(e) => {
                              e.stopPropagation();
                              onDeleteChat(chat.id);
                              setShowMenuFor(null);
                            }}
                          >
                            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                              <path d="M4 4L12 12M12 4L4 12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                            </svg>
                            <span>Delete</span>
                          </button>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
            <div className="sidebar-footer">
              <button className="settings-btn" onClick={onSettings}>
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M8 10C9.10457 10 10 9.10457 10 8C10 6.89543 9.10457 6 8 6C6.89543 6 6 6.89543 6 8C6 9.10457 6.89543 10 8 10Z" stroke="currentColor" strokeWidth="1.5" />
                  <path d="M12.5 8C12.5 7.5 12.7 7 12.9 6.6L13.8 5.1C14 4.7 13.9 4.2 13.6 3.9L12.1 2.4C11.8 2.1 11.3 2 10.9 2.2L9.4 3.1C9 3.3 8.5 3.3 8 3.3C7.5 3.3 7 3.3 6.6 3.1L5.1 2.2C4.7 2 4.2 2.1 3.9 2.4L2.4 3.9C2.1 4.2 2 4.7 2.2 5.1L3.1 6.6C3.3 7 3.3 7.5 3.3 8C3.3 8.5 3.3 9 3.1 9.4L2.2 10.9C2 11.3 2.1 11.8 2.4 12.1L3.9 13.6C4.2 13.9 4.7 14 5.1 13.8L6.6 12.9C7 12.7 7.5 12.7 8 12.7C8.5 12.7 9 12.7 9.4 12.9L10.9 13.8C11.3 14 11.8 13.9 12.1 13.6L13.6 12.1C13.9 11.8 14 11.3 13.8 10.9L12.9 9.4C12.7 9 12.5 8.5 12.5 8Z" stroke="currentColor" strokeWidth="1.5" />
                </svg>
                Settings
              </button>
            </div>
          </>
        ) : (
          <div className="sidebar-collapsed-content">
            <div className="sidebar-collapsed-top">
              <button className="sidebar-icon-btn" onClick={onToggle} title="Expand sidebar">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <rect x="3" y="4" width="18" height="16" rx="2" stroke="currentColor" strokeWidth="2" />
                  <path d="M9 4V20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                </svg>
              </button>
              <button className="sidebar-icon-btn" onClick={onNewChat} title="New chat">
                <svg width="20" height="20" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M8 3V13M3 8H13" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                </svg>
              </button>
            </div>
            <div className="sidebar-collapsed-bottom">
              <button className="sidebar-icon-btn" onClick={onSettings} title="Settings">
                <svg width="20" height="20" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M8 10C9.10457 10 10 9.10457 10 8C10 6.89543 9.10457 6 8 6C6.89543 6 6 6.89543 6 8C6 9.10457 6.89543 10 8 10Z" stroke="currentColor" strokeWidth="1.5" />
                  <path d="M12.5 8C12.5 7.5 12.7 7 12.9 6.6L13.8 5.1C14 4.7 13.9 4.2 13.6 3.9L12.1 2.4C11.8 2.1 11.3 2 10.9 2.2L9.4 3.1C9 3.3 8.5 3.3 8 3.3C7.5 3.3 7 3.3 6.6 3.1L5.1 2.2C4.7 2 4.2 2.1 3.9 2.4L2.4 3.9C2.1 4.2 2 4.7 2.2 5.1L3.1 6.6C3.3 7 3.3 7.5 3.3 8C3.3 8.5 3.3 9 3.1 9.4L2.2 10.9C2 11.3 2.1 11.8 2.4 12.1L3.9 13.6C4.2 13.9 4.7 14 5.1 13.8L6.6 12.9C7 12.7 7.5 12.7 8 12.7C8.5 12.7 9 12.7 9.4 12.9L10.9 13.8C11.3 14 11.8 13.9 12.1 13.6L13.6 12.1C13.9 11.8 14 11.3 13.8 10.9L12.9 9.4C12.7 9 12.5 8.5 12.5 8Z" stroke="currentColor" strokeWidth="1.5" />
                </svg>
              </button>
            </div>
          </div>
        )}
      </div>
    </>
  );
};

export default Sidebar;

