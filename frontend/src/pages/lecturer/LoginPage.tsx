import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../../api/client';

export const LoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('******');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    const val = username.trim().toLowerCase();

    // Giả lập phân quyền trực tiếp ở Frontend khớp với tài khoản mẫu
    if (val === 'admin' || val === 'pdt') {
      localStorage.setItem('access_token', 'mock_token_admin_123');
      localStorage.setItem('user_role', val === 'admin' ? 'ADMIN' : 'TRAINING_OFFICE');
      localStorage.setItem('username', val);
      navigate('/admin');
    } else if (val === 'gv001' || val.startsWith('gv')) {
      localStorage.setItem('access_token', 'mock_token_lecturer_123');
      localStorage.setItem('user_role', 'LECTURER');
      localStorage.setItem('username', val);
      navigate('/lecturer');
    } else {
      setError('Tài khoản không tồn tại! Vui lòng dùng: admin, pdt hoặc gv001');
    }
  };
  const quickFill = (user: string) => {
    setUsername(user);
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-6 bg-slate-900">
      <div className="bg-white rounded-3xl shadow-2xl max-w-md w-full p-8 border border-slate-700/50">
        <div className="text-center mb-6">
          <h1 className="text-2xl font-bold text-slate-900">Cổng Đào Tạo & Xếp Lịch HUIT</h1>
          <p className="text-xs text-slate-500 mt-1">Hệ thống Xếp lịch tự động GA</p>
        </div>

        {error && <div className="mb-4 p-3 bg-rose-50 text-rose-600 text-xs rounded-xl font-medium">{error}</div>}

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase mb-1">Tên đăng nhập</label>
            <input 
              type="text" 
              value={username} 
              onChange={(e) => setUsername(e.target.value)} 
              required 
              placeholder="admin, pdt hoặc gv001" 
              className="w-full bg-slate-50 border rounded-xl px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-indigo-600"
            />
          </div>
          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase mb-1">Mật khẩu</label>
            <input 
              type="password" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)} 
              required 
              className="w-full bg-slate-50 border rounded-xl px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-indigo-600"
            />
          </div>
          <button type="submit" className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3.5 rounded-xl shadow-lg transition text-sm">
            Đăng nhập hệ thống
          </button>
        </form>

        <div className="mt-6 pt-6 border-t text-center">
          <p className="text-xs text-slate-500 mb-2">Đăng nhập nhanh tài khoản mẫu:</p>
          <div className="flex gap-2 justify-center">
            <button onClick={() => quickFill('admin')} className="px-3 py-1.5 bg-slate-100 hover:bg-indigo-50 text-indigo-700 rounded-lg text-xs font-semibold">🛡️ Admin</button>
            <button onClick={() => quickFill('gv001')} className="px-3 py-1.5 bg-slate-100 hover:bg-indigo-50 text-indigo-700 rounded-lg text-xs font-semibold">👨‍🏫 Giảng viên (gv001)</button>
          </div>
        </div>
      </div>
    </div>
  );
};