import React, { useState, useEffect } from 'react';
import './ThinkingIndicator.css';
import { useTheme } from '../context/ThemeContext';

const ThinkingIndicator = () => {
  const { theme } = useTheme();
  const [displayText, setDisplayText] = useState('');
  const fullText = 'thinking...';
  const [charIndex, setCharIndex] = useState(0);

  useEffect(() => {
    if (charIndex < fullText.length) {
      const timeout = setTimeout(() => {
        setDisplayText(fullText.substring(0, charIndex + 1));
        setCharIndex(charIndex + 1);
      }, 100); // Speed of typewriter effect

      return () => clearTimeout(timeout);
    } else {
      // Reset after completing to loop continuously
      const resetTimeout = setTimeout(() => {
        setDisplayText('');
        setCharIndex(0);
      }, 1500); // Wait before restarting

      return () => clearTimeout(resetTimeout);
    }
  }, [charIndex, fullText]);

  return (
    <div className={`thinking-indicator theme-${theme}`}>
      <span className="thinking-text">{displayText}</span>
      {charIndex < fullText.length && <span className="thinking-cursor">|</span>}
    </div>
  );
};

export default ThinkingIndicator;

