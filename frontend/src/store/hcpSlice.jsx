import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const fetchHCPs = createAsyncThunk('hcp/fetchHCPs', async () => {
  const response = await axios.get(`${API_URL}/hcps`);
  return response.data.hcps;
});

export const fetchInteractions = createAsyncThunk('hcp/fetchInteractions', async () => {
  const response = await axios.get(`${API_URL}/interactions`);
  return response.data.interactions;
});

export const logInteraction = createAsyncThunk('hcp/logInteraction', async (data) => {
  const response = await axios.post(`${API_URL}/interactions/log`, data);
  return response.data;
});

export const sendChat = createAsyncThunk('hcp/sendChat', async ({ message, history }) => {
  const response = await axios.post(`${API_URL}/chat`, { message, history });
  return response.data;
});

const hcpSlice = createSlice({
  name: 'hcp',
  initialState: {
    hcps: [],
    interactions: [],
    loading: false,
    error: null,
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchHCPs.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchHCPs.fulfilled, (state, action) => {
        state.loading = false;
        state.hcps = action.payload;
      })
      .addCase(fetchHCPs.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      })
      .addCase(fetchInteractions.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchInteractions.fulfilled, (state, action) => {
        state.loading = false;
        state.interactions = action.payload;
      })
      .addCase(fetchInteractions.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      })
      .addCase(logInteraction.rejected, (state, action) => {
        state.error = action.error.message;
      })
      .addCase(sendChat.rejected, (state, action) => {
        state.error = action.error.message;
      });
  },
});

export default hcpSlice.reducer;