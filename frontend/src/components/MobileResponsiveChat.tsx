import React, { useState, useEffect } from 'react';
import { useMediaQuery } from '../hooks/useMediaQuery';
import RagChatImproved from './RagChatImproved';

const MobileResponsiveChat = () => {
  const isMobile = useMediaQuery(768);
  const isTablet = useMediaQuery(1024);
  const [isMounted, setIsMounted] = useState(false);

  // Ensure component is mounted before rendering to prevent SSR issues
  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) {
    return (
      <div className="flex items-center justify-center h-full w-full">
        <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  return (
    <React.Suspense fallback={
      <div className="flex items-center justify-center h-full w-full">
        <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-indigo-500"></div>
      </div>
    }>
      <div className={`h-full w-full flex flex-col overflow-hidden ${isMobile ? 'p-1' : isTablet ? 'p-2' : 'p-3'}`}>
        {/* Using a wrapper to ensure the chat component fits properly in the modal */}
        <div className="h-full w-full overflow-auto">
          <RagChatImproved />
        </div>
      </div>
    </React.Suspense>
  );
};

export default MobileResponsiveChat;