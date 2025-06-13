import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { fetchSessions } from './store/slices/sessionsSlice';
import { wsService } from './services/api';
import Sidebar from './components/Sidebar';
import Chat from './components/Chat';
import './styles/glass-ui.css';

const App = () => {
    const dispatch = useDispatch();
    const [isSidebarOpen, setIsSidebarOpen] = useState(false);
    const { currentSessionId } = useSelector(state => state.sessions);

    useEffect(() => {
        dispatch(fetchSessions());
        wsService.connect();
    }, [dispatch]);

    const toggleSidebar = () => {
        setIsSidebarOpen(!isSidebarOpen);
    };

    return (
        <div className="app-container">
            <Sidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />
            
            <main className="main-content">
                <header className="glass-header">
                    <button className="glass-menu-btn" onClick={toggleSidebar}>
                        <span className="menu-icon"></span>
                    </button>
                    <h1 className="glass-title">Agent AI</h1>
                    <div className="glass-actions">
                        <button className="glass-btn">Ustawienia</button>
                    </div>
                </header>

                <div className="content-area">
                    {currentSessionId ? (
                        <Chat />
                    ) : (
                        <div className="glass-panel welcome-panel">
                            <div className="panel-title" data-emoji="👋">Witaj w Agent AI</div>
                            <p>Wybierz sesję z menu po lewej stronie lub utwórz nową, aby rozpocząć rozmowę z agentem.</p>
                        </div>
                    )}
                </div>
            </main>
        </div>
    );
};

export default App;
