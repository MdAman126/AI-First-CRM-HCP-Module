import { configureStore } from '@reduxjs/toolkit';
import hcpReducer from './hcpSlice';

export const store = configureStore({
  reducer: {
    hcp: hcpReducer,
  },
});