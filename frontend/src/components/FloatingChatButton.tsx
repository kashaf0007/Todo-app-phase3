import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { usePathname } from 'next/navigation';
import { useMediaQuery } from '../hooks/useMediaQuery';

// Dynamically import the mobile-responsive chat component
const MobileResponsiveChat = dynamic(() => import('./MobileResponsiveChat'), { ssr: false });

const FloatingChatButton = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isVisible, setIsVisible] = useState(false);
  const isMobile = useMediaQuery(768);
  const isTablet = useMediaQuery(1024);
  const pathname = usePathname();

  // Don't show on login/signup pages
  const excludedPaths = ['/login', '/signup'];
  const shouldShow = !pathname || !excludedPaths.some(path => pathname.startsWith(path));

  if (!shouldShow) {
    return null;
  }

  const toggleChat = () => {
    if (!isOpen) {
      setIsOpen(true);
    } else {
      setIsVisible(false);
      setTimeout(() => setIsOpen(false), 300); // Match the transition duration
    }
  };

  const closeChat = () => {
    setIsVisible(false);
    setTimeout(() => setIsOpen(false), 300); // Match the transition duration
  };

  // Handle Escape key press to close the chat
  useEffect(() => {
    const handleEsc = (event) => {
      if (event.keyCode === 27 && isOpen) {
        closeChat();
      }
    };

    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [isOpen]);

  // Determine modal dimensions based on device size
  const getModalDimensions = () => {
    if (isMobile) {
      return 'h-full max-h-full rounded-none'; // Full height on mobile, remove all rounding
    } else if (isTablet) {
      return 'h-[75vh] max-h-[700px] max-w-md rounded-2xl'; // Medium height on tablet
    } else {
      return 'h-[80vh] max-h-[800px] max-w-lg rounded-2xl'; // Fixed height on desktop with rounded corners
    }
  };

  return (
    <>
      {/* Floating button - Enhanced FAB with improved styling */}
      <button
        onClick={toggleChat}
        className="fixed bottom-6 right-6 z-50 bg-gradient-to-r from-indigo-600 via-purple-600 to-blue-600 text-white rounded-full shadow-xl hover:shadow-2xl active:scale-95 transition-all duration-300 ease-in-out transform hover:scale-110 focus:outline-none focus:ring-4 focus:ring-indigo-400 focus:ring-opacity-50 w-14 h-14 md:w-16 md:h-16 flex items-center justify-center border-2 border-white group"
        aria-label="Open AI Chatbot"
      >
        <div className="relative">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-7 w-7 transition-transform duration-300 group-hover:rotate-12"
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
          {/* Notification badge */}
          {!isOpen && (
            <div className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center border-2 border-white">
              <span className="text-xs text-white font-bold">!</span>
            </div>
          )}
        </div>
      </button>

      {/* Chat Modal - Only renders when isOpen is true */}
      {isOpen && (
        <div
          className={`fixed inset-0 z-50 flex items-center justify-center p-2 sm:p-4 bg-gradient-to-br from-black/60 to-black/80 backdrop-blur-md transition-opacity duration-300 ${
            isVisible ? 'opacity-100' : 'opacity-0'
          }`}
          onClick={closeChat} // Close when clicking on the backdrop
        >
          <div
            className={`relative w-full max-w-full ${getModalDimensions()} bg-gradient-to-b from-white to-gray-50 shadow-2xl overflow-hidden flex flex-col transform transition-all duration-300 ease-in-out ${
              isVisible ? 'translate-y-0 opacity-100 scale-100' : 'translate-y-8 opacity-0 scale-90'
            }`}
            onClick={(e) => e.stopPropagation()} // Prevent closing when clicking inside the modal
          >
            {/* Enhanced header with gradient */}
            <div className="bg-gradient-to-r from-indigo-600 to-purple-600 p-3 sm:p-4 flex justify-between items-center">
              <div className="flex items-center gap-2">
                <div className="bg-white/20 p-2 rounded-lg">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-5 w-5 text-white"
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
                </div>
                <h3 className="text-white font-semibold text-sm sm:text-base">AI Assistant</h3>
              </div>

              <button
                onClick={closeChat}
                className="text-white/80 hover:text-white hover:bg-white/20 rounded-full p-2 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-white/50"
                aria-label="Close chat"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-5 w-5"
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

            {/* Chat content */}
            <div className="flex-grow overflow-hidden">
              <MobileResponsiveChat />
            </div>

            {/* Footer with additional info */}
            <div className="border-t border-gray-200 bg-gray-50 p-2 sm:p-3 text-center">
              <p className="text-xs text-gray-500 flex items-center justify-center gap-1.5">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                <span className="text-xs sm:text-[0.65rem]">Powered by RAG Technology</span>
              </p>
            </div>
          </div>
        </div>
      )}
      {/* Effect to trigger the animation when the modal opens */}
      {isOpen && !isVisible && setTimeout(() => setIsVisible(true), 10)}
    </>
  );
};

export default FloatingChatButton;