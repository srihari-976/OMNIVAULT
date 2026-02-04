import React from 'react';
import './PrivacyPolicy.css';
import { useTheme } from '../context/ThemeContext';

const PrivacyPolicy = ({ onClose }) => {
  const { theme } = useTheme();

  return (
    <div className="policy-overlay" onClick={onClose}>
      <div className={`policy-modal theme-${theme}`} onClick={(e) => e.stopPropagation()}>
        <div className="policy-header">
          <h2>Privacy Policy</h2>
          <button className="close-btn" onClick={onClose}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </button>
        </div>
        <div className="policy-content">
          <div className="policy-section">
            <h3>1. Introduction</h3>
            <p>
              OMNIVAULT is an offline chatbot application that operates completely locally on your device. 
              This privacy policy explains how we handle your data and ensure your privacy.
            </p>
          </div>

          <div className="policy-section">
            <h3>2. Offline Operation</h3>
            <p>
              OMNIVAULT is designed to work completely offline. All processing, including interactions with 
              LLaMA models and RAG (Retrieval Augmented Generation) functionality, occurs locally on your device. 
              No data is transmitted to external servers.
            </p>
          </div>

          <div className="policy-section">
            <h3>3. Data Storage</h3>
            <p>
              All chat history, uploaded files, and conversation data are stored locally on your device. 
              We do not collect, store, or transmit any personal information to external servers.
            </p>
          </div>

          <div className="policy-section">
            <h3>4. File Handling</h3>
            <p>
              When you upload photos or files, they are processed locally using RAG technology. Files are 
              indexed and stored on your device only. No file content is shared with external services.
            </p>
          </div>

          <div className="policy-section">
            <h3>5. Model Processing</h3>
            <p>
              LLaMA models run entirely on your local machine. All AI processing happens offline, ensuring 
              complete privacy and data security. No conversation data leaves your device.
            </p>
          </div>

          <div className="policy-section">
            <h3>6. No Data Collection</h3>
            <p>
              We do not collect, track, or analyze any user data. There are no analytics, cookies, or 
              tracking mechanisms. Your conversations remain completely private.
            </p>
          </div>

          <div className="policy-section">
            <h3>7. Updates and Changes</h3>
            <p>
              This privacy policy may be updated from time to time. Any changes will be reflected in this 
              document. Continued use of OMNIVAULT constitutes acceptance of the updated policy.
            </p>
          </div>

          <div className="policy-section">
            <h3>8. Contact</h3>
            <p>
              If you have any questions about this privacy policy, please refer to the application settings 
              or documentation.
            </p>
          </div>

          <div className="policy-footer">
            <p>Last updated: {new Date().toLocaleDateString()}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PrivacyPolicy;

