import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';
const WS_BASE_URL = 'ws://localhost:8765';

// Konfiguracja axios
axios.defaults.baseURL = API_BASE_URL;

// Interceptor do obsługi błędów
axios.interceptors.response.use(
    response => response,
    error => {
        console.error('API Error:', error);
        return Promise.reject(error);
    }
);

// API dla agentów
export const agentsApi = {
    getAgents: () => axios.get('/api/agents'),
    startAgent: (agentId) => axios.post(`/api/agents/${agentId}/start`),
    stopAgent: (agentId) => axios.post(`/api/agents/${agentId}/stop`),
    getAgentStatus: (agentId) => axios.get(`/api/agents/${agentId}/status`)
};

// API dla workflow
export const workflowsApi = {
    getWorkflows: () => axios.get('/api/workflows'),
    createWorkflow: (workflow) => axios.post('/api/workflows', workflow),
    updateWorkflow: (workflowId, workflow) => axios.put(`/api/workflows/${workflowId}`, workflow),
    deleteWorkflow: (workflowId) => axios.delete(`/api/workflows/${workflowId}`),
    runWorkflow: (workflowId) => axios.post(`/api/workflows/${workflowId}/run`)
};

// API dla sesji
export const sessionsApi = {
    getSessions: () => axios.get('/api/sessions'),
    createSession: (sessionData) => axios.post('/api/sessions', sessionData),
    getSessionMessages: (sessionId) => axios.get(`/api/sessions/${sessionId}/messages`),
    saveMessage: (sessionId, message) => axios.post(`/api/sessions/${sessionId}/messages`, message)
};

// Klasa do obsługi WebSocket
class WebSocketService {
    constructor() {
        this.socket = null;
        this.subscribers = new Set();
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
    }

    connect() {
        try {
            this.socket = new WebSocket(WS_BASE_URL);
            
            this.socket.onopen = () => {
                console.log('WebSocket connected');
                this.reconnectAttempts = 0;
                this.notifySubscribers({ type: 'connection', status: 'connected' });
            };

            this.socket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.notifySubscribers(data);
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };

            this.socket.onclose = () => {
                console.log('WebSocket disconnected');
                this.notifySubscribers({ type: 'connection', status: 'disconnected' });
                this.attemptReconnect();
            };

            this.socket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.notifySubscribers({ type: 'connection', status: 'error', error });
            };
        } catch (error) {
            console.error('Error connecting to WebSocket:', error);
            this.attemptReconnect();
        }
    }

    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            setTimeout(() => {
                console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
                this.connect();
            }, this.reconnectDelay * this.reconnectAttempts);
        } else {
            console.error('Max reconnection attempts reached');
            this.notifySubscribers({ type: 'connection', status: 'failed' });
        }
    }

    subscribe(callback) {
        this.subscribers.add(callback);
        return () => this.subscribers.delete(callback);
    }

    notifySubscribers(data) {
        this.subscribers.forEach(callback => callback(data));
    }

    send(message) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify(message));
        } else {
            console.error('WebSocket is not connected');
        }
    }

    disconnect() {
        if (this.socket) {
            this.socket.close();
        }
    }
}

export const wsService = new WebSocketService(); 