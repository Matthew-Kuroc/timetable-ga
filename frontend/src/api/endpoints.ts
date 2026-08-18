import apiClient from './client';

export const authApi = {
  login: async (username: string, password: string) => {
    // FastAPI OAuth2PasswordRequestForm yêu cầu định dạng URLSearchParams
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', password);

    const response = await apiClient.post('/auth/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    
    // Lưu token và role vào localStorage
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('user_role', response.data.role); // ADMIN, TRAINING_OFFICE, LECTURER
      localStorage.setItem('username', username);
    }
    return response.data;
  },
};