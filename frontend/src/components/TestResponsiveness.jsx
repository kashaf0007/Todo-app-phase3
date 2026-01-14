import React, { useState } from 'react';
import FloatingChatButton from './FloatingChatButton';

const TestResponsiveness = () => {
  const [screenSize, setScreenSize] = useState('desktop'); // 'mobile', 'tablet', 'desktop'

  const getContainerClass = () => {
    switch(screenSize) {
      case 'mobile':
        return 'w-full h-screen max-w-[400px] mx-auto border-4 border-blue-500 rounded-lg relative overflow-hidden';
      case 'tablet':
        return 'w-full h-screen max-w-[800px] mx-auto border-4 border-green-500 rounded-lg relative overflow-hidden';
      case 'desktop':
      default:
        return 'w-full h-screen border-4 border-purple-500 rounded-lg relative overflow-hidden';
    }
  };

  const getScreenLabel = () => {
    switch(screenSize) {
      case 'mobile':
        return '📱 Mobile View (375px)';
      case 'tablet':
        return '📱 Tablet View (768px)';
      case 'desktop':
      default:
        return '🖥️ Desktop View (Full Width)';
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold text-center mb-6 text-gray-800">Chatbot Responsiveness Test</h1>
        
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4 text-gray-700">Select Screen Size:</h2>
          <div className="flex flex-wrap gap-3 justify-center">
            <button
              onClick={() => setScreenSize('mobile')}
              className={`px-4 py-2 rounded-lg font-medium ${
                screenSize === 'mobile'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Mobile (375px)
            </button>
            <button
              onClick={() => setScreenSize('tablet')}
              className={`px-4 py-2 rounded-lg font-medium ${
                screenSize === 'tablet'
                  ? 'bg-green-500 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Tablet (768px)
            </button>
            <button
              onClick={() => setScreenSize('desktop')}
              className={`px-4 py-2 rounded-lg font-medium ${
                screenSize === 'desktop'
                  ? 'bg-purple-500 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Desktop
            </button>
          </div>
          
          <div className="mt-4 text-center text-gray-600">
            <p>Current view: <span className="font-semibold">{getScreenLabel()}</span></p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-lg font-semibold mb-4 text-gray-700">Testing Area</h2>
          <p className="text-gray-600 mb-4">
            The chatbot should appear in the bottom-right corner. Resize the simulated screen using the buttons above to test responsiveness.
          </p>
          
          <div className={getContainerClass()}>
            <div className="absolute inset-0 bg-gradient-to-br from-gray-50 to-gray-100 p-4">
              <div className="h-full flex flex-col">
                <header className="bg-indigo-600 text-white p-4 rounded-t-lg">
                  <h2 className="text-lg font-bold">Test Page</h2>
                  <p className="text-indigo-200 text-sm">This simulates a page with the responsive chatbot</p>
                </header>
                
                <div className="flex-1 bg-white p-4 overflow-y-auto">
                  <div className="space-y-4">
                    <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                      <h3 className="font-semibold text-blue-800">Sample Content</h3>
                      <p className="text-blue-600">This is sample content to simulate a real page with the chatbot floating on top.</p>
                    </div>
                    
                    <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                      <h3 className="font-semibold text-green-800">More Content</h3>
                      <p className="text-green-600">Additional content to show how the chatbot behaves on pages with varying content heights.</p>
                    </div>
                    
                    <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
                      <h3 className="font-semibold text-purple-800">Even More Content</h3>
                      <p className="text-purple-600">This demonstrates scrolling behavior and how the chatbot remains accessible.</p>
                    </div>
                    
                    <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
                      <h3 className="font-semibold text-yellow-800">Final Section</h3>
                      <p className="text-yellow-600">Scroll down to see how the chatbot stays positioned correctly.</p>
                    </div>
                  </div>
                </div>
                
                <footer className="bg-gray-100 p-4 text-center text-gray-600 text-sm border-t border-gray-200">
                  Footer content
                </footer>
              </div>
              
              {/* Floating chat button will appear here */}
              <FloatingChatButton />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TestResponsiveness;