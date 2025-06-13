import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { workflowsApi } from '../../services/api';

// Async thunks
export const fetchWorkflows = createAsyncThunk(
  'workflows/fetchWorkflows',
  async () => {
    const response = await workflowsApi.getWorkflows();
    return response.data;
  }
);

export const createWorkflow = createAsyncThunk(
  'workflows/createWorkflow',
  async (workflow) => {
    const response = await workflowsApi.createWorkflow(workflow);
    return response.data;
  }
);

export const updateWorkflow = createAsyncThunk(
  'workflows/updateWorkflow',
  async ({ workflowId, workflow }) => {
    const response = await workflowsApi.updateWorkflow(workflowId, workflow);
    return response.data;
  }
);

export const deleteWorkflow = createAsyncThunk(
  'workflows/deleteWorkflow',
  async (workflowId) => {
    await workflowsApi.deleteWorkflow(workflowId);
    return workflowId;
  }
);

export const runWorkflow = createAsyncThunk(
  'workflows/runWorkflow',
  async (workflowId) => {
    const response = await workflowsApi.runWorkflow(workflowId);
    return response.data;
  }
);

const initialState = {
  workflows: [],
  status: 'idle', // 'idle' | 'loading' | 'succeeded' | 'failed'
  error: null,
  runningWorkflows: {}, // Map of workflowId to status
};

const workflowsSlice = createSlice({
  name: 'workflows',
  initialState,
  reducers: {
    updateWorkflowStatus: (state, action) => {
      const { workflowId, status } = action.payload;
      state.runningWorkflows[workflowId] = status;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchWorkflows.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchWorkflows.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.workflows = action.payload;
      })
      .addCase(fetchWorkflows.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.error.message;
      })
      .addCase(createWorkflow.fulfilled, (state, action) => {
        state.workflows.push(action.payload);
      })
      .addCase(updateWorkflow.fulfilled, (state, action) => {
        const index = state.workflows.findIndex(w => w.id === action.payload.id);
        if (index !== -1) {
          state.workflows[index] = action.payload;
        }
      })
      .addCase(deleteWorkflow.fulfilled, (state, action) => {
        state.workflows = state.workflows.filter(w => w.id !== action.payload);
      })
      .addCase(runWorkflow.fulfilled, (state, action) => {
        state.runningWorkflows[action.payload.workflowId] = 'running';
      });
  },
});

export const { updateWorkflowStatus } = workflowsSlice.actions;
export default workflowsSlice.reducer; 