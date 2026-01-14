import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

const ChatPage = () => {
  const [userInput, setUserInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [userId, setUserId] = useState('');
  const [conversationId, setConversationId] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [showTaskPanel, setShowTaskPanel] = useState(false);
  const messagesEndRef = useRef(null);

  // Initialize with a random user ID (in a real app, this would come from auth)
  useEffect(() => {
    const randomUserId = `user_${Date.now()}`;
    setUserId(randomUserId);
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!userInput.trim() || isLoading) return;

    // Add user message to the chat
    const userMessage = { role: 'user', content: userInput, timestamp: new Date() };
    setMessages(prev => [...prev, userMessage]);
    setUserInput('');
    setIsLoading(true);

    try {
      // Send message to backend
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/api/${userId}/chat`,
        {
          conversation_id: conversationId,
          message: userInput
        },
        {
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );

      const { conversation_id, response: botResponse, tool_calls } = response.data;

      // Update conversation ID if it's the first message
      if (!conversationId) {
        setConversationId(conversation_id);
      }

      // Add bot response to the chat
      const botMessage = {
        role: 'assistant',
        content: botResponse,
        tool_calls: tool_calls,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, botMessage]);

      // Update tasks if any task-related operations occurred
      if (tool_calls && tool_calls.length > 0) {
        const taskOperations = tool_calls.filter(call =>
          call.tool_name.includes('task')
        );
        if (taskOperations.length > 0) {
          // Refresh tasks after operations
          refreshTasks();
        }
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your request.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const refreshTasks = async () => {
    try {
      const response = await axios.get(
        `${process.env.NEXT_PUBLIC_API_URL}/api/${userId}/tasks`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth-token') || ''}`,
            'Content-Type': 'application/json'
          }
        }
      );
      setTasks(response.data);
    } catch (error) {
      console.error('Error fetching tasks:', error);
    }
  };

  useEffect(() => {
    // Load tasks when component mounts
    refreshTasks();
  }, []);

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const toggleTaskPanel = () => {
    setShowTaskPanel(!showTaskPanel);
  };

  /* Responsive UI Features:
 * - Mobile-first design with stacked layout on small screens
 * - Side-by-side layout on medium screens and above
 * - Collapsible task panel that becomes a slide-over on mobile
 * - Adaptive text sizing and padding for different screen sizes
 * - Flexible grid layouts that adjust based on available space
 */
return (
    <div className="flex flex-col h-screen max-h-[100svh] bg-gradient-to-br from-gray-50 to-gray-100 rounded-none sm:rounded-2xl shadow-none sm:shadow-xl overflow-hidden border border-gray-200">
      {/* Header */}
      <header className="bg-gradient-to-r from-indigo-600 via-purple-600 to-blue-600 text-white p-3 sm:p-4">
        <div className="flex flex-col sm:flex-row justify-between items-center gap-3 sm:gap-4">
          <div className="flex-1 flex items-center gap-2 sm:gap-3">
            <div className="bg-white/20 p-2 rounded-lg sm:rounded-xl backdrop-blur-sm">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-1 w-1 sm:h-6 sm:w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
            </div>
            <div>
              <h1 className="text-medium sm:text-xl md:text-2xl font-bold">RAG Todo Chatbot</h1>
              <p className="text-indigo-200 text-xs sm:text-sm">Manage your tasks with natural language</p>
            </div>
          </div>
          <button
            onClick={toggleTaskPanel}
            className="bg-white/20 hover:bg-white/30 text-white px-3 py-1.5 sm:px-4 sm:py-2 rounded-lg sm:rounded-xl transition-all duration-300 flex items-center gap-1 sm:gap-2 whitespace-nowrap shadow-md hover:shadow-lg text-sm"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            {showTaskPanel ? 'Hide Tasks' : 'Show Tasks'}
          </button>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden flex-col md:flex-row">
        {/* Mobile Task Panel - Slide-over */}
        {showTaskPanel && (
          <div className="md:hidden fixed inset-0 z-40 bg-black/50 backdrop-blur-sm flex justify-end p-2">
            <div className="w-full max-w-sm sm:max-w-md bg-white shadow-2xl rounded-t-2xl p-4 sm:p-5 overflow-y-auto max-h-[calc(100vh-2rem)] transform transition-transform duration-300 ease-in-out">
              <div className="flex justify-between items-center mb-3 sm:mb-5 pb-2 sm:pb-3 border-b border-gray-200">
                <h2 className="text-lg sm:text-xl font-bold text-gray-800 flex items-center gap-2">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 sm:h-5 sm:w-5 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                  Your Tasks
                </h2>
                <button
                  onClick={toggleTaskPanel}
                  className="text-gray-500 hover:text-gray-700 p-1 rounded-full hover:bg-gray-100"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              {tasks.length === 0 ? (
                <div className="text-center py-6 sm:py-8">
                  <div className="mx-auto bg-gray-100 p-3 sm:p-4 rounded-full w-14 h-14 sm:w-16 sm:h-16 flex items-center justify-center mb-3 sm:mb-4">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 sm:h-8 sm:w-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                  </div>
                  <p className="text-gray-500 text-sm sm:text-center">No tasks yet. Add some tasks using the chat!</p>
                </div>
              ) : (
                <div className="space-y-3 sm:space-y-4">
                  {tasks.map((task) => (
                    <div
                      key={task.id}
                      className={`p-3 sm:p-4 rounded-xl sm:rounded-2xl border transition-all duration-300 ${
                        task.completed
                          ? 'bg-gradient-to-r from-green-50 to-emerald-50 border-green-200'
                          : 'bg-gradient-to-r from-white to-gray-50 border-gray-200 hover:shadow-md'
                      }`}
                    >
                      <div className="flex justify-between items-start">
                        <div className="flex-1 min-w-0">
                          <h3 className={`font-medium sm:font-semibold truncate ${
                            task.completed ? 'line-through text-gray-500' : 'text-gray-800'
                          }`}>
                            {task.title}
                          </h3>
                          {task.description && (
                            <p className="text-xs sm:text-sm text-gray-600 mt-1 sm:mt-2 truncate">{task.description}</p>
                          )}
                          <div className="flex flex-wrap gap-1 sm:gap-2 mt-2 sm:mt-3">
                            {task.priority && (
                              <span className={`text-[0.6rem] sm:text-xs px-1 py-0.5 sm:px-2.5 sm:py-1 rounded-full ${
                                task.priority === 'HIGH'
                                  ? 'bg-red-100 text-red-800'
                                  : task.priority === 'MEDIUM'
                                    ? 'bg-yellow-100 text-yellow-800'
                                    : 'bg-green-100 text-green-800'
                              }`}>
                                {task.priority}
                              </span>
                            )}
                            {task.category && (
                              <span className="text-[0.6rem] sm:text-xs px-1 py-0.5 sm:px-2.5 sm:py-1 rounded-full bg-blue-100 text-blue-800">
                                {task.category}
                              </span>
                            )}
                            {task.status && (
                              <span className="text-[0.6rem] sm:text-xs px-1 py-0.5 sm:px-2.5 sm:py-1 rounded-full bg-purple-100 text-purple-800">
                                {task.status.replace('_', ' ')}
                              </span>
                            )}
                            {task.due_date && (
                              <span className="text-[0.6rem] sm:text-xs px-1 py-0.5 sm:px-2.5 sm:py-1 rounded-full bg-gray-100 text-gray-800 flex items-center gap-1">
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-2 w-2 sm:h-3 sm:w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                </svg>
                                {new Date(task.due_date).toLocaleDateString()}
                              </span>
                            )}
                          </div>
                        </div>
                        <div className="ml-2 sm:ml-3 flex-shrink-0 flex items-center">
                          <input
                            type="checkbox"
                            checked={task.completed}
                            onChange={() => {}}
                            className="h-4 w-4 sm:h-5 sm:w-5 text-indigo-600 rounded focus:ring-indigo-500 border-gray-300"
                            disabled
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Desktop Task Panel */}
        <div className={`${showTaskPanel ? 'hidden md:flex' : 'hidden'} md:w-1/3 lg:w-1/4 xl:w-1/5 bg-gradient-to-b from-white to-gray-50 p-3 sm:p-4 overflow-y-auto max-h-[calc(100svh-4rem)] md:max-h-none border-r border-gray-200 flex-col`}>
          <div className="w-full">
            <div className="flex justify-between items-center mb-3 sm:mb-5 pb-2 sm:pb-3 border-b border-gray-200">
              <h2 className="text-lg sm:text-xl font-bold text-gray-800 flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 sm:h-5 sm:w-5 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                Your Tasks
              </h2>
              <button
                onClick={toggleTaskPanel}
                className="text-gray-500 hover:text-gray-700 md:hidden p-1 rounded-full hover:bg-gray-100"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            {tasks.length === 0 ? (
              <div className="text-center py-6 sm:py-8 flex-1 flex flex-col justify-center">
                <div className="mx-auto bg-gray-100 p-3 sm:p-4 rounded-full w-14 h-14 sm:w-16 sm:h-16 flex items-center justify-center mb-3 sm:mb-4">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 sm:h-8 sm:w-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2 a2 2 0 012 2" />
                  </svg>
                </div>
                <p className="text-gray-500 text-sm sm:text-center">No tasks yet. Add some tasks using the chat!</p>
              </div>
            ) : (
              <div className="space-y-3 sm:space-y-4 flex-1 overflow-y-auto">
                {tasks.map((task) => (
                  <div
                    key={task.id}
                    className={`p-3 sm:p-4 rounded-xl sm:rounded-2xl border transition-all duration-300 ${
                      task.completed
                        ? 'bg-gradient-to-r from-green-50 to-emerald-50 border-green-200'
                        : 'bg-gradient-to-r from-white to-gray-50 border-gray-200 hover:shadow-md'
                    }`}
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1 min-w-0">
                        <h3 className={`font-medium sm:font-semibold truncate ${
                          task.completed ? 'line-through text-gray-500' : 'text-gray-800'
                        }`}>
                          {task.title}
                        </h3>
                        {task.description && (
                          <p className="text-xs sm:text-sm text-gray-600 mt-1 sm:mt-2 truncate">{task.description}</p>
                        )}
                        <div className="flex flex-wrap gap-1 sm:gap-2 mt-2 sm:mt-3">
                          {task.priority && (
                            <span className={`text-[0.6rem] sm:text-xs px-1 py-0.5 sm:px-2.5 sm:py-1 rounded-full ${
                              task.priority === 'HIGH'
                                ? 'bg-red-100 text-red-800'
                                : task.priority === 'MEDIUM'
                                  ? 'bg-yellow-100 text-yellow-800'
                                  : 'bg-green-100 text-green-800'
                            }`}>
                              {task.priority}
                            </span>
                          )}
                          {task.category && (
                            <span className="text-[0.6rem] sm:text-xs px-1 py-0.5 sm:px-2.5 sm:py-1 rounded-full bg-blue-100 text-blue-800">
                              {task.category}
                            </span>
                          )}
                          {task.status && (
                            <span className="text-[0.6rem] sm:text-xs px-1 py-0.5 sm:px-2.5 sm:py-1 rounded-full bg-purple-100 text-purple-800">
                              {task.status.replace('_', ' ')}
                            </span>
                          )}
                          {task.due_date && (
                            <span className="text-[0.6rem] sm:text-xs px-1 py-0.5 sm:px-2.5 sm:py-1 rounded-full bg-gray-100 text-gray-800 flex items-center gap-1">
                              <svg xmlns="http://www.w3.org/2000/svg" className="h-2 w-2 sm:h-3 sm:w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                              </svg>
                              {new Date(task.due_date).toLocaleDateString()}
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="ml-2 sm:ml-3 flex-shrink-0 flex items-center">
                        <input
                          type="checkbox"
                          checked={task.completed}
                          onChange={() => {}}
                          className="h-4 w-4 sm:h-5 sm:w-5 text-indigo-600 rounded focus:ring-indigo-500 border-gray-300"
                          disabled
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Chat Container */}
        <div className={`${showTaskPanel ? 'md:w-2/3 lg:w-3/4 xl:w-4/5' : 'w-full'} flex flex-col bg-gradient-to-b from-white to-gray-50 flex-1`}>
          {/* Conversation Context Indicator */}
          <div className="border-b border-gray-200 p-2 sm:p-3 bg-gradient-to-r from-blue-50/50 to-indigo-50/50 backdrop-blur-sm">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-1 sm:gap-2 text-xs sm:text-sm">
              <div className="text-gray-600 break-all max-w-[70%] flex items-center gap-1 sm:gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 sm:h-4 sm:w-4 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
                {conversationId ? (
                  <span>Conv: {conversationId.substring(0, 8)}...</span>
                ) : (
                  <span>New conversation</span>
                )}
              </div>
              <div className="text-gray-600 break-all max-w-[70%] flex items-center gap-1 sm:gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 sm:h-4 sm:w-4 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                {userId && <span>User: {userId.substring(0, 8)}...</span>}
              </div>
            </div>
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-3 sm:p-4 space-y-3 sm:space-y-4" style={{ maxHeight: 'calc(100svh - 120px)' }}>
            {messages.length === 0 ? (
              <div className="text-center text-gray-600 mt-6 sm:mt-10 px-2 sm:px-4">
                <div className="mx-auto bg-gradient-to-br from-indigo-100 to-purple-100 p-4 sm:p-5 rounded-full w-16 h-16 sm:w-20 sm:h-20 flex items-center justify-center mb-4 sm:mb-6">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 sm:h-10 sm:w-10 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                  </svg>
                </div>
                <h3 className="text-lg sm:text-xl font-bold text-gray-800 mb-2 sm:mb-3">Welcome to the RAG Todo Chatbot!</h3>
                <p className="mb-4 sm:mb-6 text-gray-600 text-sm sm:text-base">How can I help you manage your tasks today?</p>
                <div className="grid grid-cols-1 gap-3 sm:gap-4 max-w-xs sm:max-w-2xl mx-auto">
                  <div className="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-lg sm:rounded-xl p-3 sm:p-4 text-left border border-indigo-100 shadow-sm text-xs sm:text-sm">
                    <p className="font-semibold text-indigo-700 flex items-center gap-1 sm:gap-2">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 sm:h-4 sm:w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                      Try: "Add a task to buy Groceries"
                    </p>
                  </div>
                  <div className="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-lg sm:rounded-xl p-3 sm:p-4 text-left border border-indigo-100 shadow-sm text-xs sm:text-sm">
                    <p className="font-semibold text-indigo-700 flex items-center gap-1 sm:gap-2">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 sm:h-4 sm:w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                      Or: "Show me my tasks"
                    </p>
                  </div>
                  <div className="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-lg sm:rounded-xl p-3 sm:p-4 text-left border border-indigo-100 shadow-sm text-xs sm:text-sm">
                    <p className="font-semibold text-indigo-700 flex items-center gap-1 sm:gap-2">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 sm:h-4 sm:w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                      Also: "Mark task 1 as complete"
                    </p>
                  </div>
                  <div className="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-lg sm:rounded-xl p-3 sm:p-4 text-left border border-indigo-100 shadow-sm text-xs sm:text-sm">
                    <p className="font-semibold text-indigo-700 flex items-center gap-1 sm:gap-2">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 sm:h-4 sm:w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                      And: "What did I ask before?"
                    </p>
                  </div>
                </div>
                <p className="mt-4 sm:mt-8 text-xs sm:text-sm text-gray-500 flex items-center justify-center gap-1 sm:gap-2">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 sm:h-4 sm:w-4 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  This chatbot remembers your conversation history.
                </p>
              </div>
            ) : (
              <div className="space-y-3 sm:space-y-4">
                {messages.map((msg, index) => (
                  <div
                    key={index}
                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[90%] rounded-2xl sm:rounded-3xl p-3 sm:p-4 transition-all duration-300 ${
                        msg.role === 'user'
                          ? 'bg-gradient-to-br from-indigo-500 to-purple-600 text-white rounded-br-none shadow-lg'
                          : 'bg-gradient-to-br from-gray-100 to-gray-200 text-gray-800 rounded-bl-none shadow'
                      } hover:shadow-xl`}
                    >
                      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-1 sm:gap-2 mb-1 sm:mb-2">
                        <div className="flex items-center gap-1 sm:gap-2">
                          {msg.role === 'user' ? (
                            <div className="bg-white/20 p-1 rounded-full">
                              <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 sm:h-4 sm:w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                              </svg>
                            </div>
                          ) : (
                            <div className="bg-white/20 p-1 rounded-full">
                              <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 sm:h-4 sm:w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                              </svg>
                            </div>
                          )}
                          <span className={`text-xs sm:text-sm font-medium ${msg.role === 'user' ? 'text-indigo-100' : 'text-gray-600'}`}>
                            {msg.role === 'user' ? 'You' : 'Assistant'}
                          </span>
                        </div>
                        <span className={`text-xs ${msg.role === 'user' ? 'text-indigo-200' : 'text-gray-500'}`}>
                          {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                      </div>
                      <div className={`prose prose-sm max-w-none text-xs sm:text-sm ${msg.role === 'user' ? 'text-white' : 'text-gray-800'}`}>
                        {msg.content.split('\n').map((line, i) => (
                          <p key={i} className="mb-2 last:mb-0">{line}</p>
                        ))}
                      </div>

                      {msg.tool_calls && msg.tool_calls.length > 0 && (
                        <div className="mt-3 pt-3 border-t border-white/30">
                          <div className="text-xs sm:text-sm font-medium mb-2 flex items-center gap-2">
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-2.573 1.066c-.94 1.543.826 3.31 2.37 2.37a1.724 1.724 0 002.572 1.065c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 00-2.573-1.066c-1.543-.94-3.31.826-2.37 2.37a1.724 1.724 0 00-1.065 2.572c-1.756.426-1.756 2.924 0 3.35z" />
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                            </svg>
                            Tools used:
                          </div>
                          {msg.tool_calls.map((tool, idx) => (
                            <div key={idx} className="text-xs sm:text-sm opacity-90 break-all bg-black/5 p-2 rounded-lg mb-1 last:mb-0">
                              <span className="font-mono bg-white/20 px-2 py-0.5 rounded text-[0.7rem]">{tool.tool_name}</span>
                              <span className="ml-2">with args: {JSON.stringify(tool.arguments)}</span>
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Context indicator for assistant messages */}
                      {msg.role === 'assistant' && (
                        <div className="mt-3 flex items-center text-xs sm:text-sm opacity-80">
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 mr-1.5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          <span>Using conversation context</span>
                        </div>
                      )}

                      {/* Task summary for assistant messages that involve tasks */}
                      {msg.role === 'assistant' && (
                        <div className="mt-3 flex flex-wrap gap-2">
                          {msg.content.toLowerCase().includes('task') && msg.content.toLowerCase().includes('created') && (
                            <div className="inline-flex items-center bg-green-500/20 text-green-700 text-xs px-2.5 py-1.5 rounded-full">
                              <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                              </svg>
                              Task created
                            </div>
                          )}
                          {msg.content.toLowerCase().includes('task') && msg.content.toLowerCase().includes('complete') && (
                            <div className="inline-flex items-center bg-blue-500/20 text-blue-700 text-xs px-2.5 py-1.5 rounded-full">
                              <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                              </svg>
                              Task completed
                            </div>
                          )}
                          {msg.content.toLowerCase().includes('task') && msg.content.toLowerCase().includes('deleted') && (
                            <div className="inline-flex items-center bg-red-500/20 text-red-700 text-xs px-2.5 py-1.5 rounded-full">
                              <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                              </svg>
                              Task deleted
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area - Fixed at bottom on mobile */}
          <div className="p-3 sm:p-4 border-t border-gray-200 bg-gradient-to-b from-gray-50 to-white sticky bottom-0">
            <div className="flex flex-col gap-3">
              <div className="flex flex-col gap-3">
                <textarea
                  value={userInput}
                  onChange={(e) => setUserInput(e.target.value)}
                  onKeyDown={handleKeyPress}
                  placeholder="Type your message here (e.g., 'Add a task to buy groceries', 'What was my last task?', 'Complete the shopping task')..."
                  className="w-full border border-gray-300 rounded-lg sm:rounded-xl p-3 sm:p-4 min-h-[60px] max-h-40 resize-none focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent shadow-sm text-sm"
                  disabled={isLoading}
                  rows="1"
                />
                <button
                  onClick={handleSendMessage}
                  disabled={isLoading || !userInput.trim()}
                  className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-4 py-2.5 sm:px-5 sm:py-3.5 rounded-lg sm:rounded-xl hover:from-indigo-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50 flex items-center justify-center w-full sm:w-auto sm:self-end shadow-md hover:shadow-lg transition-all duration-300 text-sm"
                >
                  {isLoading ? (
                    <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                  ) : (
                    <span className="flex items-center">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 sm:h-5 sm:w-5 mr-1 sm:mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
                      </svg>
                      Send Message
                    </span>
                  )}
                </button>
              </div>
            </div>
            <div className="mt-2 sm:mt-3 text-xs sm:text-sm text-gray-500 flex flex-col sm:flex-row justify-between items-center gap-2">
              <div className="flex flex-wrap gap-2 sm:gap-3 justify-center sm:justify-start">
                {userId && <span className="break-all max-w-[100px] sm:max-w-none flex items-center gap-1"><svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg> User: {userId.substring(0, 8)}...</span>}
                {conversationId && <span className="break-all max-w-[100px] sm:max-w-none flex items-center gap-1"><svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" /></svg> Conv: {conversationId.substring(0, 8)}...</span>}
              </div>
              <div className="inline-flex items-center gap-1.5 bg-blue-50 px-2.5 sm:px-3 py-1 sm:py-1.5 rounded-full">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5 sm:h-4 sm:w-4 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                <span>Context-aware</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;
