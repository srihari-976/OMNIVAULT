import React, { useState, useEffect } from 'react';
import './Settings.css';
import { useTheme } from '../context/ThemeContext';
import PrivacyPolicy from './PrivacyPolicy';
import TermsOfUse from './TermsOfUse';

const Settings = ({ onClose }) => {
  const [showPrivacy, setShowPrivacy] = useState(false);
  const [showTerms, setShowTerms] = useState(false);
  const { theme, setTheme } = useTheme();
  const [activeTab, setActiveTab] = useState('general');
  const [chatHistory, setChatHistory] = useState(() => {
    const saved = localStorage.getItem('omnivault-chat-history');
    return saved !== null ? saved === 'true' : true;
  });
  const [sharedLinks, setSharedLinks] = useState(() => {
    const saved = localStorage.getItem('omnivault-shared-links');
    return saved !== null ? saved === 'true' : true;
  });
  const [language, setLanguage] = useState(() => {
    return localStorage.getItem('omnivault-language') || 'English';
  });

  useEffect(() => {
    localStorage.setItem('omnivault-chat-history', chatHistory);
  }, [chatHistory]);

  useEffect(() => {
    localStorage.setItem('omnivault-shared-links', sharedLinks);
  }, [sharedLinks]);

  useEffect(() => {
    localStorage.setItem('omnivault-language', language);
  }, [language]);

  const handleThemeChange = (newTheme) => {
    setTheme(newTheme);
  };

  return (
    <div className="settings-overlay" onClick={onClose}>
      <div className={`settings-modal theme-${theme}`} onClick={(e) => e.stopPropagation()}>
        <div className="settings-header">
          <h2>Settings</h2>
          <button className="close-btn" onClick={onClose}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </button>
        </div>
        <div className="settings-content">
          <div className="settings-tabs">
            <button
              className={`tab ${activeTab === 'general' ? 'active' : ''}`}
              onClick={() => setActiveTab('general')}
            >
              General
            </button>
            <button
              className={`tab ${activeTab === 'data' ? 'active' : ''}`}
              onClick={() => setActiveTab('data')}
            >
              Data controls
            </button>
            <button
              className={`tab ${activeTab === 'about' ? 'active' : ''}`}
              onClick={() => setActiveTab('about')}
            >
              About
            </button>
          </div>
          <div className="settings-body">
            {activeTab === 'general' && (
              <div className="settings-section">
                <h3>Appearance</h3>
                <div className="setting-item">
                  <div className="setting-info">
                    <label>Theme</label>
                    <p>Choose how OMNIVAULT looks to you.</p>
                  </div>
                  <select 
                    className="setting-control"
                    value={theme}
                    onChange={(e) => handleThemeChange(e.target.value)}
                  >
                    <option value="dark">Dark</option>
                    <option value="light">Light</option>
                  </select>
                </div>
                <h3>Language</h3>
                <div className="setting-item">
                  <div className="setting-info">
                    <label>Display language</label>
                    <p>Select your preferred language for the interface.</p>
                  </div>
                  <select 
                    className="setting-control"
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                  >
                    <option value="English">English</option>
                    <option value="Spanish">Spanish</option>
                    <option value="French">French</option>
                    <option value="German">German</option>
                    <option value="Italian">Italian</option>
                    <option value="Portuguese">Portuguese</option>
                    <option value="Chinese">Chinese</option>
                    <option value="Japanese">Japanese</option>
                  </select>
                </div>
              </div>
            )}
            {activeTab === 'data' && (
              <div className="settings-section">
                <h3>Chat History & Training</h3>
                <div className="setting-item">
                  <div className="setting-info">
                    <label>Chat history</label>
                    <p>When chat history is disabled, we'll save new conversations on your device and won't use them to improve our models.</p>
                  </div>
                  <label className="toggle-switch">
                    <input 
                      type="checkbox" 
                      checked={chatHistory}
                      onChange={(e) => setChatHistory(e.target.checked)}
                    />
                    <span className="slider"></span>
                  </label>
                </div>
                <div className="setting-item">
                  <div className="setting-info">
                    <label>Shared links</label>
                    <p>When enabled, you can share links to your conversations.</p>
                  </div>
                  <label className="toggle-switch">
                    <input 
                      type="checkbox" 
                      checked={sharedLinks}
                      onChange={(e) => setSharedLinks(e.target.checked)}
                    />
                    <span className="slider"></span>
                  </label>
                </div>
              </div>
            )}
            {activeTab === 'about' && (
              <div className="settings-section">
                <h3>About OMNIVAULT</h3>
                <div className="setting-item">
                  <div className="setting-info">
                    <label>Version</label>
                    <p>OMNIVAULT v1.0.0</p>
                  </div>
                </div>
                <div className="setting-item">
                  <div className="setting-info">
                    <label>Terms of use</label>
                    <p>Read our terms of use</p>
                  </div>
                  <button className="link-button" onClick={() => setShowTerms(true)}>
                    View
                  </button>
                </div>
                <div className="setting-item">
                  <div className="setting-info">
                    <label>Privacy policy</label>
                    <p>Read our privacy policy</p>
                  </div>
                  <button className="link-button" onClick={() => setShowPrivacy(true)}>
                    View
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
      {showPrivacy && <PrivacyPolicy onClose={() => setShowPrivacy(false)} />}
      {showTerms && <TermsOfUse onClose={() => setShowTerms(false)} />}
    </div>
  );
};

export default Settings;

