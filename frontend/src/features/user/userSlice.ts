import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface UserState {
  isAuthenticated: boolean;
  isLoading: boolean;
  accessToken: string | null;
  refreshToken: string | null;
  userInfo: {
    id: number;
    username: string;
    email: string;
    role: string;
    avatar?: string;
  } | null;
}

const initialState: UserState = {
  isAuthenticated: false,
  isLoading: true,
  accessToken: null,
  refreshToken: null,
  userInfo: null,
};

const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    loginSuccess(state, action: PayloadAction<{ accessToken: string; refreshToken: string; userInfo: any }>) {
      state.isAuthenticated = true;
      state.isLoading = false;
      state.accessToken = action.payload.accessToken;
      state.refreshToken = action.payload.refreshToken;
      state.userInfo = action.payload.userInfo;
    },
    logout(state) {
      state.isAuthenticated = false;
      state.isLoading = false;
      state.accessToken = null;
      state.refreshToken = null;
      state.userInfo = null;
    },
    setUserInfo(state, action: PayloadAction<any>) {
      state.userInfo = action.payload;
    },
    setLoading(state, action: PayloadAction<boolean>) {
      state.isLoading = action.payload;
    },
  },
});

export const { loginSuccess, logout, setUserInfo, setLoading } = userSlice.actions;
export default userSlice.reducer; 