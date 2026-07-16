import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import './App.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const ADMIN_API_KEY = import.meta.env.VITE_ADMIN_API_KEY || 'admin-secret-key-123456';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [tutorId, setTutorId] = useState<number | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [tutors, setTutors] = useState<any[]>([]);
  const [showAdmin, setShowAdmin] = useState(false);
  const [selectedTutor, setSelectedTutor] = useState<number | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const tutorParam = params.get('tutor');
    if (tutorParam) {
      const id = parseInt(tutorParam);
      setTutorId(id);
      setSelectedTutor(id);
    }
    const sessionParam = params.get('session');
    if (sessionParam) {
      setSessionId(sessionParam);
    }
    loadTutors();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadTutors = async () => {
    try {
      const response = await axios.get(`${API_URL}/tutors`, {
        headers: { 'admin-api-key': ADMIN_API_KEY }
      });
      setTutors(response.data);
      if (response.data.length > 0 && !selectedTutor) {
        setSelectedTutor(response.data[0].id);
        setTutorId(response.data[0].id);
      }
    } catch (error) {
      console.error('Error loading tutors:', error);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || !tutorId) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_URL}/chat`, {
        message: input,
        tutor_id: tutorId,
        session_id: sessionId
      });

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.data.response
      };
      setMessages(prev => [...prev, assistantMessage]);
      
      if (response.data.session_id) {
        setSessionId(response.data.session_id);
      }
    } catch (error: any) {
      const errorMessage: Message = {
        role: 'assistant',
        content: `⚠️ Error: ${error.response?.data?.detail || error.message || 'Unknown error'}`
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const startNewConversation = () => {
    setMessages([]);
    setSessionId(null);
  };

  return (
    <div className="app-container">
      <div className="chat-header">
        <h2>
          {tutors.find(t => t.id === selectedTutor)?.name || 'Tutor Chat'}
        </h2>
        <div className="header-actions">
          <button onClick={startNewConversation} className="new-chat-btn">
            ✨ New Chat
          </button>
          <button onClick={() => setShowAdmin(!showAdmin)} className="admin-toggle-btn">
            {showAdmin ? '✕ Close' : '⚙️ Admin'}
          </button>
        </div>
      </div>

      {showAdmin && (
        <div className="admin-panel">
          <h3>📚 Available Tutors</h3>
          <button onClick={loadTutors} className="load-tutors-btn">🔄 Refresh</button>
          <div className="tutor-list">
            {tutors.length === 0 ? (
              <p className="no-tutors">No tutors found. Create one via API.</p>
            ) : (
              tutors.map(tutor => (
                <div
                  key={tutor.id}
                  className={`tutor-item ${selectedTutor === tutor.id ? 'selected' : ''}`}
                  onClick={() => {
                    setSelectedTutor(tutor.id);
                    setTutorId(tutor.id);
                    setMessages([]);
                    setSessionId(null);
                  }}
                >
                  <strong>{tutor.name}</strong>
                  <p>{tutor.description || 'No description'}</p>
                  <span className={`status ${tutor.status ? 'active' : 'inactive'}`}>
                    {tutor.status ? '✅ Active' : '⛔ Inactive'}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="empty-state">
            <p>💬 Start a conversation with the tutor!</p>
            <p className="hint">Ask anything about the topic they're trained on.</p>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.role}`}>
              <div className="message-content">
                <ReactMarkdown>{msg.content}</ReactMarkdown>
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="message assistant loading">
            <div className="message-content">⏳ Thinking...</div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-container">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message..."
          disabled={isLoading || !tutorId}
          rows={2}
        />
        <button onClick={handleSend} disabled={isLoading || !input.trim() || !tutorId}>
          Send
        </button>
      </div>

      <div className="footer">
        <small>Tutor ID: {tutorId || 'None'} | Session: {sessionId?.slice(0, 8) || 'New'}</small>
      </div>
    </div>
  );
}

export default App;
