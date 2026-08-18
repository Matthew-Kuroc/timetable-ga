import { useNavigate } from 'react-router-dom';

export const Navbar = () => {
  const navigate = useNavigate();
  const username = localStorage.getItem('username') || 'User';
  const role = localStorage.getItem('user_role') || 'GUEST';

  const handleLogout = () => {
    localStorage.clear();
    navigate('/login');
  };

  return (
    <header className="bg-indigo-900 text-white shadow-md z-20">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-indigo-600 flex items-center justify-center font-bold text-lg">H</div>
          <div>
            <h1 className="font-bold text-base">Cổng Thông Tin Hệ Thống Xếp Lịch GA</h1>
            <p className="text-xs text-indigo-300">Đại học Công Thương TP.HCM (HUIT)</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="bg-indigo-800/80 px-3 py-1.5 rounded-lg border border-indigo-700 text-xs font-medium flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
            <span>{username} ({role})</span>
          </div>
          <button 
            onClick={handleLogout} 
            className="bg-rose-600 hover:bg-rose-700 text-white text-xs font-semibold px-4 py-2 rounded-lg transition shadow-sm"
          >
            Đăng xuất
          </button>
        </div>
      </div>
    </header>
  );
};