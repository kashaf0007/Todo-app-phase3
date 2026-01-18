import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import apiClient from '../lib/axios-instance';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  tool_calls?: any[];
}

interface Task {
  id: string;
  title: string;
  description?: string;
  priority?: string;
  category?: string;
  status?: string;
  due_date?: string;
  completed: boolean;
}

const RagChatImproved = () => {
  const [userInput, setUserInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [userId, setUserId] = useState('');
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [showTaskPanel, setShowTaskPanel] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Initialize with user ID from auth system
  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      try {
        // Decode JWT to get user ID
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
          return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));

        const decodedToken = JSON.parse(jsonPayload);
        setUserId(decodedToken.sub); // 'sub' is the standard claim for subject (user ID)
      } catch (error) {
        console.error('Error decoding token:', error);
        // Fallback to a temporary ID if token decoding fails
        setUserId(`temp_user_${Date.now()}`);
      }
    } else {
      // If no token, use a temporary ID
      setUserId(`temp_user_${Date.now()}`);
    }
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!userInput.trim() || isLoading) return;

    // Add user message to the chat
    const userMessage: Message = { role: 'user', content: userInput, timestamp: new Date() };
    setMessages(prev => [...prev, userMessage]);
    setUserInput('');
    setIsLoading(true);

    try {
      // Send message to backend using the configured API client
      const response = await apiClient.post(
        `/api/${userId}/chat`,
        {
          conversation_id: conversationId,
          message: userInput
        }
      );

      const { conversation_id, response: botResponse, tool_calls } = response.data;

      // Update conversation ID if it's the first message
      if (!conversationId) {
        setConversationId(conversation_id);
      }

      // Add bot response to the chat
      const botMessage: Message = {
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

      let errorMessageText = 'Sorry, I encountered an error processing your request.';

      // Handle different types of errors
      if (axios.isAxiosError(error)) {
        if (error.code === 'ERR_NETWORK') {
          errorMessageText = 'Network error: Unable to connect to the server. Please check if the backend is running and accessible.';
        } else if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
          errorMessageText = 'Request timeout: The server took too long to respond. Please try again.';
        } else if (error.response) {
          // Server responded with error status
          console.error('Server error details:', error.response.data);

          // Check if it's a validation error from FastAPI
          if (error.response.status === 422) {
            errorMessageText = `Validation error: ${error.response.data?.detail?.[0]?.msg || 'Invalid input provided.'}`;
          } else {
            errorMessageText = `Server error (${error.response.status}): ${error.response.data?.detail || 'An error occurred on the server.'}`;

            // If it's a 500 error, provide more specific guidance
            if (error.response.status === 500) {
              errorMessageText += ' This might be due to the backend server not running or misconfigured environment variables (e.g., COHERE_API_KEY).';
            }
          }
        } else if (error.request) {
          // Request was made but no response received
          errorMessageText = 'Connection error: No response received from the server. Please check your network connection and ensure the backend is running.';
        }
      } else if (error instanceof Error) {
        errorMessageText = error.message;
      }

      const errorMessage: Message = {
        role: 'assistant',
        content: errorMessageText,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const refreshTasks = async () => {
    if (!userId) {
      // Don't fetch tasks if userId is not set yet
      return;
    }

    try {
      const response = await apiClient.get(`/api/${userId}/tasks`);
      setTasks(response.data);
    } catch (error) {
      console.error('Error fetching tasks:', error);
    }
  };

  useEffect(() => {
    // Load tasks when component mounts
    refreshTasks();
  }, []);

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const toggleTaskPanel = () => {
    setShowTaskPanel(!showTaskPanel);
  };

  // Auto-resize textarea based on content
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 150)}px`;
    }
  }, [userInput]);

  return (
    <>
      {/* Laptop/desktop floating popup */}
      <div className="hidden md:block fixed bottom-4 right-4 z-50">
        <div className="flex flex-col h-[600px] w-[400px] max-w-full bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-200 flex-1 transition-all duration-300 hover:shadow-2xl">


          <div className="flex flex-1 overflow-hidden flex-col md:flex-row">
             {/* Task Panel - Mobile view (hidden on desktop)  */}
            {showTaskPanel && (
              <div className="md:hidden fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex justify-end p-2">
                <div className="w-full max-w-xs sm:max-w-sm md:max-w-md bg-white shadow-xl rounded-t-xl p-4 overflow-y-auto max-h-[80vh] transform transition-transform duration-300 ease-in-out">
                  <div className="flex justify-between items-center mb-3 pb-2 border-b border-gray-200">
                    <h2 className="text-base font-bold text-gray-800">Your Tasks</h2>
                    <button
                      onClick={toggleTaskPanel}
                      className="text-gray-500 hover:text-gray-700 p-1 rounded-full hover:bg-gray-100 transition-colors text-lg font-bold"
                    >
                      ×
                    </button>
                  </div>
                  {tasks.length === 0 ? (
                    <div className="text-center py-6">
                      <p className="text-gray-500 text-sm">No tasks yet. Add some tasks using the chat!</p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {tasks.map((task) => (
                        <div
                          key={task.id}
                          className={`p-3 rounded-xl border text-xs ${
                            task.completed
                              ? 'bg-green-50 border-green-200'
                              : 'bg-white border-gray-200'
                          }`}
                        >
                          <div className="flex flex-col sm:flex-row justify-between items-start gap-2">
                            <div className="flex-1 min-w-0">
                              <h3 className={`font-medium truncate ${
                                task.completed ? 'line-through text-gray-500' : 'text-gray-800'
                              }`}>
                                {task.title}
                              </h3>
                              {task.description && (
                                <p className="text-xs text-gray-600 mt-1 truncate">{task.description}</p>
                              )}
                              <div className="flex flex-wrap gap-1 mt-2">
                                {task.priority && (
                                  <span className={`text-[0.6rem] px-1.5 py-0.5 rounded-full ${
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
                                  <span className="text-[0.6rem] px-1.5 py-0.5 rounded-full bg-blue-100 text-blue-800">
                                    {task.category}
                                  </span>
                                )}
                                {task.status && (
                                  <span className="text-[0.6rem] px-1.5 py-0.5 rounded-full bg-purple-100 text-purple-800">
                                    {task.status.replace('_', ' ')}
                                  </span>
                                )}
                                {task.due_date && (
                                  <span className="text-[0.6rem] px-1.5 py-0.5 rounded-full bg-gray-100 text-gray-800">
                                    {new Date(task.due_date).toLocaleDateString()}
                                  </span>
                                )}
                              </div>
                            </div>
                            <div className="ml-2 flex-shrink-0 flex items-center">
                              <input
                                type="checkbox"
                                checked={task.completed}
                                onChange={() => {}}
                                className="h-4 w-4 text-indigo-600 rounded focus:ring-indigo-500 border-gray-300"
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
            <div className={`${showTaskPanel ? 'hidden md:flex' : 'hidden'} w-full md:w-1/2 lg:w-2/5 xl:w-1/3 bg-white p-3 overflow-y-auto max-h-[calc(100vh-8rem)] border-r border-gray-200`}>
              <div className="w-full">
                <div className="flex justify-between items-center mb-3 pb-2 border-b border-gray-200">
                  <h2 className="text-base font-bold text-gray-800">Your Tasks</h2>
                </div>
                {tasks.length === 0 ? (
                  <div className="text-center py-6">
                    <p className="text-gray-500 text-sm">No tasks yet. Add some tasks using the chat!</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {tasks.map((task) => (
                      <div
                        key={task.id}
                        className={`p-3 rounded-xl border text-xs ${
                          task.completed
                            ? 'bg-green-50 border-green-200'
                            : 'bg-white border-gray-200'
                        }`}
                      >
                        <div className="flex flex-col sm:flex-row justify-between items-start gap-2">
                          <div className="flex-1 min-w-0">
                            <h3 className={`font-medium truncate ${
                              task.completed ? 'line-through text-gray-500' : 'text-gray-800'
                            }`}>
                              {task.title}
                            </h3>
                            {task.description && (
                              <p className="text-xs text-gray-600 mt-1 truncate">{task.description}</p>
                            )}
                            <div className="flex flex-wrap gap-1 mt-2">
                              {task.priority && (
                                <span className={`text-[0.6rem] px-1.5 py-0.5 rounded-full ${
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
                                <span className="text-[0.6rem] px-1.5 py-0.5 rounded-full bg-blue-100 text-blue-800">
                                  {task.category}
                                </span>
                              )}
                              {task.status && (
                                <span className="text-[0.6rem] px-1.5 py-0.5 rounded-full bg-purple-100 text-purple-800">
                                  {task.status.replace('_', ' ')}
                                </span>
                              )}
                              {task.due_date && (
                                <span className="text-[0.6rem] px-1.5 py-0.5 rounded-full bg-gray-100 text-gray-800">
                                  {new Date(task.due_date).toLocaleDateString()}
                                </span>
                              )}
                            </div>
                          </div>
                          <div className="ml-2 flex-shrink-0 flex items-center">
                            <input
                              type="checkbox"
                              checked={task.completed}
                              onChange={() => {}}
                              className="h-4 w-4 text-indigo-600 rounded focus:ring-indigo-500 border-gray-300"
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
            <div className={`${showTaskPanel ? 'md:w-1/2 lg:w-3/5 xl:w-2/3' : 'w-full'} flex flex-col bg-white flex-1 min-h-0 relative`}>
              {/* Conversation Context Indicator */}
              <div className="border-b border-gray-200 p-4 bg-gradient-to-r from-indigo-50 to-purple-50">
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-1 text-sm">
                  <div className="text-gray-600 break-all max-w-[70%]">
                    {conversationId ? (
                      <span className="truncate font-medium">Conv: {conversationId.substring(0, 8)}...</span>
                    ) : (
                      <span className="font-medium">New conversation</span>
                    )}
                  </div>
                  <div className="text-gray-600 break-all max-w-[70%] mt-1 sm:mt-0">
                    {userId && <span className="truncate font-medium">User: {userId.substring(0, 8)}...</span>}
                  </div>
                </div>
              </div>

              {/* Messages Area */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gradient-to-b from-white to-gray-50">
                {messages.length === 0 ? (
                  <div className="text-center text-gray-600 mt-6 px-2">
                    <h3 className="text-xl font-bold text-gray-800 mb-2">Welcome to the RAG Todo Chatbot!</h3>
                    <p className="mb-4 text-sm text-gray-600">How can I help you manage your tasks today?</p>
                    <div className="grid grid-cols-1 gap-3 max-w-xs mx-auto">
                      <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-2xl p-4 text-left border border-indigo-100 shadow-sm transition-all duration-200 hover:shadow-md">
                        <p className="font-medium text-indigo-700">
                          Try: "Add a task to buy groceries"
                        </p>
                      </div>
                      <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-2xl p-4 text-left border border-indigo-100 shadow-sm transition-all duration-200 hover:shadow-md">
                        <p className="font-medium text-indigo-700">
                          Or: "Show me my tasks"
                        </p>
                      </div>
                      <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-2xl p-4 text-left border border-indigo-100 shadow-sm transition-all duration-200 hover:shadow-md">
                        <p className="font-medium text-indigo-700">
                          Also: "Mark task 1 as complete"
                        </p>
                      </div>
                    </div>
                    <p className="mt-4 text-xs text-gray-500">
                      This chatbot remembers your conversation history.
                    </p>

                  </div>
                ) : (
                  <div className="space-y-4">
                    {messages.map((msg, index) => (
                      <div
                        key={index}
                        className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                      >
                        <div
                          className={`max-w-[85%] rounded-2xl p-4 transition-all duration-200 shadow-sm ${
                            msg.role === 'user'
                              ? 'bg-gradient-to-r from-indigo-500 to-indigo-600 text-white rounded-br-none'
                              : 'bg-gradient-to-r from-gray-100 to-gray-200 text-gray-800 rounded-bl-none'
                          }`}
                        >
                          <div className="flex items-center gap-2 mb-2">
                            <div className={`w-9 h-9 rounded-full flex items-center justify-center ${
                              msg.role === 'user'
                                ? 'bg-indigo-600'
                                : 'bg-gradient-to-r from-purple-500 to-indigo-500'
                            }`}>
                              {msg.role === 'user' ? (
                                <span className="text-white font-bold text-sm">U</span>
                              ) : (
                                <span className="text-white font-bold text-sm">A</span>
                              )}
                            </div>
                            <span className="text-sm font-semibold">
                              {msg.role === 'user' ? 'You' : 'Assistant'}
                            </span>
                          </div>
                          <div className="text-base break-words pl-11">{msg.content}</div>
                          <div className="text-xs opacity-80 mt-1 text-right pl-11">
                            {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </div>
                        </div>
                      </div>
                    ))}
                    {isLoading && (
                      <div className="flex justify-start">
                        <div className="max-w-[85%] rounded-2xl p-4 bg-gradient-to-r from-gray-100 to-gray-200 text-gray-800 rounded-bl-none shadow-sm">
                          <div className="flex items-center gap-2 pl-11">
                            <div className="h-2.5 w-2.5 bg-gray-500 rounded-full animate-bounce"></div>
                            <div className="h-2.5 w-2.5 bg-gray-500 rounded-full animate-bounce delay-75"></div>
                            <div className="h-2.5 w-2.5 bg-gray-500 rounded-full animate-bounce delay-150"></div>
                          </div>
                        </div>
                      </div>
                    )}
                    <div ref={messagesEndRef} />
                  </div>
                )}
              </div>

              {/* Input Area */}
              <div className="border-t border-gray-200 p-4 bg-white">
                <div className="flex flex-col sm:flex-row items-end gap-3">
                  <textarea
                    ref={textareaRef}
                    value={userInput}
                    onChange={(e) => setUserInput(e.target.value)}
                    onKeyDown={handleKeyPress}
                    placeholder="Type your message..."
                    className="flex-1 border border-gray-300 rounded-2xl px-4 py-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-indigo-300 focus:border-transparent min-h-[48px] max-h-40 shadow-sm transition-all duration-200 focus:shadow-md"
                    rows={1}
                    disabled={isLoading}
                  />
                  <button
                    onClick={handleSendMessage}
                    disabled={isLoading || !userInput.trim()}
                    className={`p-3 rounded-full shadow-md transition-all duration-200 ${
                      isLoading || !userInput.trim()
                        ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                        : 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white hover:from-indigo-600 hover:to-purple-600 hover:shadow-lg'
                    } self-start sm:self-auto`}
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      {/* Mobile chat button */}
      <div className="fixed bottom-4 right-4 z-50 md:hidden">
        <button
          onClick={toggleTaskPanel}
          className="bg-gradient-to-r from-indigo-500 to-purple-500 text-white p-4 rounded-full shadow-lg hover:from-indigo-600 hover:to-purple-600 transition-all duration-300 transform hover:scale-105"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
        </button>
      </div>
    </>
  )
};

export default RagChatImproved;
