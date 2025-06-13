import React, { useState, useEffect, useRef } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { saveMessage, addLocalMessage } from '../store/slices/sessionsSlice';
import { wsService } from '../services/api';

const Chat = () => {
    const dispatch = useDispatch();
    const messagesEndRef = useRef(null);
    const [message, setMessage] = useState('');
    const [isConnected, setIsConnected] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    
    const { messages, currentSessionId } = useSelector(state => state.sessions);

    useEffect(() => {
        const unsubscribe = wsService.subscribe(handleWebSocketMessage);
        return () => unsubscribe();
    }, []);

    const handleWebSocketMessage = (data) => {
        if (data.type === 'connection') {
            setIsConnected(data.status === 'connected');
        } else if (data.type === 'response_chunk' && data.content) {
            addMessage('agent', data.content);
        } else if (data.type === 'welcome' && data.message) {
            addMessage('system', data.message);
        }
    };

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSendMessage = async () => {
        if (!message.trim() || !isConnected) return;

        const userMessage = message.trim();
        setMessage('');
        setIsLoading(true);

        // Dodaj wiadomość użytkownika natychmiast do stanu
        if (currentSessionId) {
            dispatch(addLocalMessage({
                role: 'user',
                content: userMessage,
                metadata: {
                    timestamp: new Date().toISOString()
                }
            }));
        }

        // Zapisz wiadomość w sesji (backend)
        if (currentSessionId) {
            await dispatch(saveMessage({
                sessionId: currentSessionId,
                message: {
                    role: 'user',
                    content: userMessage,
                    metadata: {
                        timestamp: new Date().toISOString()
                    }
                }
            }));
        }

        // Wyślij wiadomość przez WebSocket
        wsService.send({
            type: 'message',
            content: userMessage
        });

        setIsLoading(false);
    };

    const handleKeyPress = (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            handleSendMessage();
        }
    };

    const addMessage = (type, content) => {
        if (currentSessionId && type !== 'system') {
            dispatch(addLocalMessage({
                role: type === 'user' ? 'user' : 'assistant',
                content,
                metadata: {
                    timestamp: new Date().toISOString()
                }
            }));
        }
    };

    const quickMessage = (text) => {
        if (isConnected) {
            setMessage(text);
            handleSendMessage();
        } else {
            addMessage('system', 'Najpierw połącz się z agentem');
        }
    };

    return (
        <div className="glass-panel">
            <div className="panel-title" data-emoji="💬">Czat z Agentem</div>
            
            <div className={`glass-status ${isConnected ? 'connected' : 'disconnected'}`}>
                <div className="status-dot"></div>
                <span>{isConnected ? 'Połączony z agentem' : 'Rozłączony z agentem'}</span>
            </div>
            
            <div className="glass-messages">
                {messages.map((msg, index) => (
                    <div key={index} className={`glass-message ${msg.role}`}>
                        {msg.content}
                    </div>
                ))}
                {isLoading && (
                    <div className="glass-message agent">
                        Przetwarzam Twoją prośbę
                        <div className="loading-dots">
                            <span></span>
                            <span></span>
                            <span></span>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>
            
            <div className="glass-quick-actions">
                <button className="glass-quick-btn" onClick={() => quickMessage('Sprawdź moje najnowsze emaile w Gmail')}>
                    📧 Sprawdź Gmail
                </button>
                <button className="glass-quick-btn" onClick={() => quickMessage('Pokaż moje spotkania na dziś w kalendarzu')}>
                    📅 Kalendarz dziś
                </button>
                <button className="glass-quick-btn" onClick={() => quickMessage('Przeanalizuj i klasyfikuj ostatnie emaile')}>
                    🧠 Analiza emaili
                </button>
                <button className="glass-quick-btn" onClick={() => quickMessage('Jakie mam dokumenty na Google Docs?')}>
                    📄 Google Docs
                </button>
            </div>
            
            <div className="glass-input-group">
                <input
                    type="text"
                    className="glass-input"
                    placeholder="Napisz wiadomość do agenta..."
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    disabled={!isConnected}
                />
                <button
                    className="glass-btn"
                    onClick={handleSendMessage}
                    disabled={!isConnected || !message.trim()}
                >
                    Wyślij
                </button>
            </div>
        </div>
    );
};

export default Chat; 