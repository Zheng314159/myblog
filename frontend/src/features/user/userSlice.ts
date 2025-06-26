import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface UserState {
  isAuthenticated: boolean;
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
      state.accessToken = action.payload.accessToken;
      state.refreshToken = action.payload.refreshToken;
      state.userInfo = action.payload.userInfo;
    },
    logout(state) {
      state.isAuthenticated = false;
      state.accessToken = null;
      state.refreshToken = null;
      state.userInfo = null;
    },
    setUserInfo(state, action: PayloadAction<any>) {
      state.userInfo = action.payload;
    },
  },
});

export const { loginSuccess, logout, setUserInfo } = userSlice.actions;
export default userSlice.reducer; 