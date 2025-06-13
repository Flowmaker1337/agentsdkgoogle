import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { createSession, switchSession } from '../store/slices/sessionsSlice';

const Sidebar = ({ isOpen, onClose }) => {
    const dispatch = useDispatch();
    const { sessions, currentSessionId } = useSelector(state => state.sessions);

    const handleNewSession = async () => {
        await dispatch(createSession({ title: 'Nowa Rozmowa' }));
    };

    const handleSwitchSession = (sessionId) => {
        dispatch(switchSession(sessionId));
    };

    return (
        <>
            <div className={`sidebar-overlay ${isOpen ? 'active' : ''}`} onClick={onClose} />
            <div className={`glass-sidebar ${isOpen ? 'open' : ''}`}>
                <div className="sidebar-header">
                    <div className="sidebar-title">🤖 Agent Sessions</div>
                    <div className="sidebar-subtitle">Historia rozmów</div>
                </div>
                
                <div className="sidebar-section">
                    <div className="sidebar-section-title">Sesje</div>
                    <button className="new-session-btn" onClick={handleNewSession}>
                        ➕ Nowa Rozmowa
                    </button>
                    <div className="sidebar-section-title" style={{ marginTop: '16px' }}>Aktywne Sesje</div>
                    <div id="activeSessions">
                        {sessions.slice(0, 3).map(session => (
                            <div 
                                key={session.id}
                                className={`session-item ${session.id === currentSessionId ? 'active' : ''}`}
                                onClick={() => handleSwitchSession(session.id)}
                            >
                                <div className="session-name">{session.title}</div>
                                <div className="session-date">
                                    {new Date(session.updated_at).toLocaleDateString('pl-PL', {
                                        day: '2-digit',
                                        month: '2-digit',
                                        hour: '2-digit',
                                        minute: '2-digit'
                                    })} ({session.message_count} wiadomości)
                                </div>
                            </div>
                        ))}
                        {sessions.length === 0 && (
                            <div className="no-sessions">Brak sesji</div>
                        )}
                    </div>
                </div>
                
                <div className="sidebar-section">
                    <div className="sidebar-section-title">Historia</div>
                    <div id="historySessions">
                        {sessions.slice(3).map(session => (
                            <div 
                                key={session.id}
                                className={`session-item ${session.id === currentSessionId ? 'active' : ''}`}
                                onClick={() => handleSwitchSession(session.id)}
                            >
                                <div className="session-name">{session.title}</div>
                                <div className="session-date">
                                    {new Date(session.updated_at).toLocaleDateString('pl-PL', {
                                        day: '2-digit',
                                        month: '2-digit',
                                        hour: '2-digit',
                                        minute: '2-digit'
                                    })} ({session.message_count} wiadomości)
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </>
    );
};

export default Sidebar; 