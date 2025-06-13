import { configureStore } from '@reduxjs/toolkit';
import agentsReducer from './slices/agentsSlice';
import workflowsReducer from './slices/workflowsSlice';
import sessionsReducer from './slices/sessionsSlice';

export const store = configureStore({
  reducer: {
    agents: agentsReducer,
    workflows: workflowsReducer,
    sessions: sessionsReducer
  },
}); 