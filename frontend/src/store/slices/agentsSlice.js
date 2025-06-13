import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { agentsApi } from '../../services/api';

// Async thunks
export const fetchAgents = createAsyncThunk(
  'agents/fetchAgents',
  async () => {
    const response = await agentsApi.getAgents();
    return response.data;
  }
);

export const startAgent = createAsyncThunk(
  'agents/startAgent',
  async (agentId) => {
    const response = await agentsApi.startAgent(agentId);
    return response.data;
  }
);

export const stopAgent = createAsyncThunk(
  'agents/stopAgent',
  async (agentId) => {
    const response = await agentsApi.stopAgent(agentId);
    return response.data;
  }
);

const initialState = {
  agents: [],
  status: 'idle', // 'idle' | 'loading' | 'succeeded' | 'failed'
  error: null,
};

const agentsSlice = createSlice({
  name: 'agents',
  initialState,
  reducers: {
    updateAgentStatus: (state, action) => {
      const { agentId, status } = action.payload;
      const agent = state.agents.find(a => a.id === agentId);
      if (agent) {
        agent.status = status;
      }
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchAgents.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchAgents.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.agents = action.payload;
      })
      .addCase(fetchAgents.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.error.message;
      })
      .addCase(startAgent.fulfilled, (state, action) => {
        const agent = state.agents.find(a => a.id === action.payload.id);
        if (agent) {
          agent.status = 'Aktywny';
        }
      })
      .addCase(stopAgent.fulfilled, (state, action) => {
        const agent = state.agents.find(a => a.id === action.payload.id);
        if (agent) {
          agent.status = 'Nieaktywny';
        }
      });
  },
});

export const { updateAgentStatus } = agentsSlice.actions;
export default agentsSlice.reducer; 