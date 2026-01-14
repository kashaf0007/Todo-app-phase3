import React, { useState } from 'react';
import dynamic from 'next/dynamic';
import { usePathname } from 'next/navigation';
import { useMediaQuery } from '../hooks/useMediaQuery';

// Dynamically import the mobile-responsive chat component
const MobileResponsiveChat = dynamic(() => import('./MobileResponsiveChat'), { ssr: false });

const FloatingChatButtonNew = () => {
  const [isOpen, setIsOpen] = useState(false);
  const isMobile = useMediaQuery(768);
  const pathname = usePathname();

  // Don't show on login/signup pages
  const excludedPaths = ['/login', '/signup'];
  const shouldShow = !pathname || !excludedPaths.some(path => pathname.startsWith(path));

  if (!shouldShow) {
    return null;
  }

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  return (
    <>
      {/* Floating toggle button */}
      <button
        onClick={toggleChat}
        className="toggle"
        aria-label="Open AI Chatbot"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-6 w-6"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
          />
        </svg>
      </button>

      {/* Chat panel */}
      <div
        className={`panel ${isOpen ? '' : 'panelHidden'}`}
      >
        {/* Header */}
        <div className="panelHeader">
          <h3 className="font-semibold">AI Assistant</h3>
          <button
            onClick={toggleChat}
            className="close-button"
            aria-label="Close chat"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Chat body - scrollable area */}
        <div className="flex-grow overflow-y-auto p-4 bg-gray-50">
          {isOpen && <MobileResponsiveChat />}
        </div>
      </div>

      {/* Overlay when panel is open */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40"
          onClick={toggleChat}
        ></div>
      )}
    </>
  );
};

export default FloatingChatButtonNew;