import React from 'react';
import './TermsOfUse.css';
import { useTheme } from '../context/ThemeContext';

const TermsOfUse = ({ onClose }) => {
  const { theme } = useTheme();

  return (
    <div className="terms-overlay" onClick={onClose}>
      <div className={`terms-modal theme-${theme}`} onClick={(e) => e.stopPropagation()}>
        <div className="terms-header">
          <h2>Terms of Use</h2>
          <button className="close-btn" onClick={onClose}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </button>
        </div>
        <div className="terms-content">
          <div className="terms-section">
            <h3>1. Acceptance of Terms</h3>
            <p>
              By using OMNIVAULT, you agree to be bound by these Terms of Use. If you do not agree to these terms, 
              please do not use the application.
            </p>
          </div>

          <div className="terms-section">
            <h3>2. Offline Operation</h3>
            <p>
              OMNIVAULT operates as an offline chatbot application. It uses LLaMA models and RAG technology 
              locally on your device. All processing occurs offline without requiring internet connectivity.
            </p>
          </div>

          <div className="terms-section">
            <h3>3. Use of Service</h3>
            <p>
              You may use OMNIVAULT for personal or commercial purposes. The application is provided "as is" 
              without warranties of any kind. You are responsible for ensuring that your use complies with 
              applicable laws and regulations.
            </p>
          </div>

          <div className="terms-section">
            <h3>4. Local Processing</h3>
            <p>
              All AI model processing, including LLaMA inference and RAG operations, happens locally on your 
              device. You are responsible for ensuring your device meets the system requirements for running 
              these models.
            </p>
          </div>

          <div className="terms-section">
            <h3>5. File Uploads</h3>
            <p>
              When uploading photos or files, you retain all rights to your content. Files are processed 
              locally using RAG technology for context-aware responses. You are responsible for ensuring 
              you have the right to upload and process any files you provide.
            </p>
          </div>

          <div className="terms-section">
            <h3>6. Limitations</h3>
            <p>
              OMNIVAULT is provided without warranty. The accuracy of AI-generated responses may vary. 
              You should verify important information independently. We are not liable for any decisions 
              made based on the application's output.
            </p>
          </div>

          <div className="terms-section">
            <h3>7. Intellectual Property</h3>
            <p>
              The OMNIVAULT application and its interface are protected by copyright. LLaMA models are subject 
              to their respective licenses. You may not reverse engineer, decompile, or disassemble the 
              application.
            </p>
          </div>

          <div className="terms-section">
            <h3>8. Modifications</h3>
            <p>
              We reserve the right to modify these terms at any time. Continued use of OMNIVAULT after changes 
              constitutes acceptance of the modified terms.
            </p>
          </div>

          <div className="terms-section">
            <h3>9. Termination</h3>
            <p>
              You may stop using OMNIVAULT at any time. We reserve the right to discontinue the application 
              or modify its features without notice.
            </p>
          </div>

          <div className="terms-footer">
            <p>Last updated: {new Date().toLocaleDateString()}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TermsOfUse;

