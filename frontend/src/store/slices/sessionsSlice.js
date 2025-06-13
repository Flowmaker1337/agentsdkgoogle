import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { sessionsApi } from '../../services/api';

// Async thunks
export const fetchSessions = createAsyncThunk(
    'sessions/fetchSessions',
    async () => {
        const response = await sessionsApi.getSessions();
        return response.data;
    }
);

export const createSession = createAsyncThunk(
    'sessions/createSession',
    async (sessionData) => {
        const response = await sessionsApi.createSession(sessionData);
        return response.data;
    }
);

export const switchSession = createAsyncThunk(
    'sessions/switchSession',
    async (sessionId) => {
        const response = await sessionsApi.getSessionMessages(sessionId);
        return {
            sessionId,
            messages: response.data
        };
    }
);

export const saveMessage = createAsyncThunk(
    'sessions/saveMessage',
    async ({ sessionId, message }) => {
        const response = await sessionsApi.saveMessage(sessionId, message);
        return response.data;
    }
);

const initialState = {
    sessions: [],
    currentSessionId: null,
    messages: [],
    status: 'idle',
    error: null
};

const sessionsSlice = createSlice({
    name: 'sessions',
    initialState,
    reducers: {
        clearMessages: (state) => {
            state.messages = [];
        },
        addLocalMessage: (state, action) => {
            state.messages.push(action.payload);
            const session = state.sessions.find(s => s.id === state.currentSessionId);
            if (session) {
                session.message_count += 1;
                session.updated_at = new Date().toISOString();
            }
        }
    },
    extraReducers: (builder) => {
        builder
            // Fetch sessions
            .addCase(fetchSessions.pending, (state) => {
                state.status = 'loading';
            })
            .addCase(fetchSessions.fulfilled, (state, action) => {
                state.status = 'succeeded';
                state.sessions = action.payload.sessions;
            })
            .addCase(fetchSessions.rejected, (state, action) => {
                state.status = 'failed';
                state.error = action.error.message;
            })
            // Create session
            .addCase(createSession.fulfilled, (state, action) => {
                state.sessions.unshift(action.payload);
                state.currentSessionId = action.payload.id;
                state.messages = [];
            })
            // Switch session
            .addCase(switchSession.fulfilled, (state, action) => {
                state.currentSessionId = action.payload.sessionId;
                state.messages = action.payload.messages;
            })
            // Save message
            .addCase(saveMessage.fulfilled, (state, action) => {
                state.messages.push(action.payload);
                const session = state.sessions.find(s => s.id === state.currentSessionId);
                if (session) {
                    session.message_count += 1;
                    session.updated_at = new Date().toISOString();
                }
            });
    }
});

export const { clearMessages, addLocalMessage } = sessionsSlice.actions;
export default sessionsSlice.reducer; 