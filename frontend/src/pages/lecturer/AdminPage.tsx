import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../api/client';

export const AdminPage = () => {
  const [adminTab, setAdminTab] = useState<'overview' | 'csv' | 'ga' | 'accounts' | 'batches'>('overview');
  
  // State lưu dữ liệu thực tế từ Backend
  const [batches, setBatches] = useState<any[]>([]);
  const [officialFiles, setOfficialFiles] = useState<any[]>([]);
  const [timetables, setTimetables] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const navigate = useNavigate();

  // Gọi API lấy dữ liệu thực tế từ Backend SQL khi load trang hoặc chuyển tab
  const fetchBackendData = async () => {
    try {
      setLoading(true);
      setError('');

      // 1. Lấy danh sách các đợt xếp lịch (Batches) từ Database SQL
      const resBatches = await apiClient.get('/batches');
      setBatches(Array.isArray(resBatches.data) ? resBatches.data : resBatches.data.items || []);

      // 2. Lấy danh sách tệp dữ liệu chính thức từ Datasets
      const resFiles = await apiClient.get('/datasets/official/files');
      setOfficialFiles(Array.isArray(resFiles.data) ? resFiles.data : resFiles.data.items || []);

      // 3. Lấy thời khóa biểu chính thức đã xuất bản từ thuật toán GA
      const resTimetables = await apiClient.get('/ga/official-timetables');
      setTimetables(Array.isArray(resTimetables.data) ? resTimetables.data : resTimetables.data.items || []);

    } catch (err) {
      console.error('Lỗi kết nối Backend:', err);
      setError('Không thể tải dữ liệu thực tế từ server FastAPI. Vui lòng kiểm tra lại Backend.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBackendData();
  }, []);

  const handleLogout = () => {
    localStorage.clear();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-800 antialiased flex flex-col">
      {/* Header */}
      <header className="bg-indigo-900 text-white shadow-md z-20">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-indigo-600 flex items-center justify-center font-bold text-lg">H</div>
            <div>
              <h1 className="font-bold text-base">Phòng Đào Tạo & Quản Trị Hệ Thống</h1>
              <p className="text-xs text-indigo-300">Đại học Công Thương TP.HCM (HUIT)</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="bg-indigo-800/80 px-3 py-1.5 rounded-lg border border-indigo-700 text-xs font-medium flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
              <span>Role: ADMIN (admin)</span>
            </div>
            <button onClick={handleLogout} className="bg-rose-600 hover:bg-rose-700 text-white text-xs font-semibold px-4 py-2 rounded-lg transition shadow-sm">
              Đăng xuất
            </button>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <div className="flex flex-1 max-w-7xl w-full mx-auto bg-slate-100">
        {/* Sidebar */}
        <aside className="w-72 bg-white border-r border-slate-200 p-6 flex flex-col justify-between shadow-xs">
          <nav className="space-y-1.5">
            <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Menu Điều Hướng</p>
            <button onClick={() => setAdminTab('overview')} className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-semibold transition text-left ${adminTab === 'overview' ? 'bg-indigo-50 text-indigo-700' : 'hover:bg-slate-50 text-slate-600'}`}>📊 Tổng quan hệ thống</button>
            <button onClick={() => setAdminTab('csv')} className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-semibold transition text-left ${adminTab === 'csv' ? 'bg-indigo-50 text-indigo-700' : 'hover:bg-slate-50 text-slate-600'}`}>📁 Quản lý dữ liệu CSV</button>
            <button onClick={() => setAdminTab('ga')} className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-semibold transition text-left ${adminTab === 'ga' ? 'bg-indigo-50 text-indigo-700' : 'hover:bg-slate-50 text-slate-600'}`}>⚙️ Cấu hình & Chạy GA</button>
            <button onClick={() => setAdminTab('batches')} className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-semibold transition text-left ${adminTab === 'batches' ? 'bg-indigo-50 text-indigo-700' : 'hover:bg-slate-50 text-slate-600'}`}>📦 Quản lý Batches SQL</button>
          </nav>
          <div className="pt-6 border-t border-slate-100">
            <div className="bg-slate-50 p-3 rounded-xl border text-center text-xs text-slate-600 font-semibold">Đồ án Tốt nghiệp 2026</div>
          </div>
        </aside>

        {/* Workspace Content */}
        <main className="flex-1 p-8 overflow-y-auto space-y-6">
          {error && (
            <div className="bg-rose-50 border border-rose-200 text-rose-700 text-xs p-4 rounded-xl">
              {error}
            </div>
          )}

          {adminTab === 'overview' && (
            <div className="space-y-6">
              <div className="flex justify-between items-center bg-gradient-to-r from-blue-900 to-indigo-900 text-white p-6 rounded-2xl shadow-lg">
                <div>
                  <span className="bg-blue-500/30 text-blue-200 text-xs px-3 py-1 rounded-full font-semibold">GA Engine</span>
                  <h2 className="text-2xl font-bold mt-2">Quản lý dữ liệu và chạy thuật toán</h2>
                </div>
                <button onClick={() => alert('Đã gửi lệnh chạy thuật toán GA tới Backend!')} className="bg-white text-indigo-900 font-bold px-5 py-2.5 rounded-xl text-sm shadow transition hover:bg-slate-100">⚡ Chạy GA mới</button>
              </div>

              <div className="grid grid-cols-3 gap-5">
                <div className="bg-white p-5 rounded-2xl border shadow-xs"><p className="text-xs font-bold text-slate-400 uppercase">Tổng số Batches (SQL)</p><p className="text-3xl font-extrabold text-indigo-600 mt-2">{batches.length}</p></div>
                <div className="bg-white p-5 rounded-2xl border shadow-xs"><p className="text-xs font-bold text-slate-400 uppercase">Tệp dữ liệu chính thức</p><p className="text-3xl font-extrabold text-emerald-600 mt-2">{officialFiles.length}</p></div>
                <div className="bg-white p-5 rounded-2xl border shadow-xs"><p className="text-xs font-bold text-slate-400 uppercase">Thời khóa biểu GA</p><p className="text-3xl font-extrabold text-blue-600 mt-2">{timetables.length}</p></div>
              </div>
            </div>
          )}

          {adminTab === 'csv' && (
            <div className="bg-white p-8 rounded-2xl border shadow-xs space-y-4">
              <h3 className="font-bold text-lg text-slate-800">📁 Dữ liệu tệp chính thức từ Backend Datasets</h3>
              {loading ? (
                <p className="text-xs text-slate-500">Đang đồng bộ dữ liệu từ server FastAPI...</p>
              ) : (
                <div className="space-y-2">
                  {officialFiles.length > 0 ? (
                    officialFiles.map((file, idx) => (
                      <div key={idx} className="p-3 bg-slate-50 border rounded-xl text-xs font-medium text-slate-700">
                        📄 {typeof file === 'string' ? file : JSON.stringify(file)}
                      </div>
                    ))
                  ) : (
                    <p className="text-xs text-slate-400 italic">Chưa có tệp dữ liệu CSV nào được lưu trong hệ thống.</p>
                  )}
                </div>
              )}
            </div>
          )}

          {adminTab === 'ga' && (
            <div className="bg-white p-8 rounded-2xl border shadow-xs space-y-4">
              <h3 className="font-bold text-lg text-slate-800">📅 Thời khóa biểu xuất bản từ thuật toán GA (Official Timetables)</h3>
              {loading ? (
                <p className="text-xs text-slate-500">Đang tải lịch từ database...</p>
              ) : (
                <div className="space-y-2">
                  {timetables.length > 0 ? (
                    timetables.map((tb, idx) => (
                      <div key={idx} className="p-3 bg-slate-50 border rounded-xl text-xs font-medium text-indigo-900">
                        ⚡ {typeof tb === 'string' ? tb : JSON.stringify(tb)}
                      </div>
                    ))
                  ) : (
                    <p className="text-xs text-slate-400 italic">Chưa có lịch chính thức nào được xuất bản từ thuật toán GA.</p>
                  )}
                </div>
              )}
            </div>
          )}

          {adminTab === 'batches' && (
            <div className="bg-white p-8 rounded-2xl border shadow-xs space-y-4">
              <h3 className="font-bold text-lg text-slate-800">📦 Danh sách các đợt xếp lịch (Batches SQL)</h3>
              {loading ? (
                <p className="text-xs text-slate-500">Đang tải danh sách batches từ backend...</p>
              ) : (
                <div className="space-y-2">
                  {batches.length > 0 ? (
                    batches.map((batch, idx) => (
                      <div key={idx} className="p-3 bg-slate-50 border rounded-xl text-xs font-semibold text-slate-800">
                        📦 Batch ID / Code: {typeof batch === 'string' ? batch : JSON.stringify(batch)}
                      </div>
                    ))
                  ) : (
                    <p className="text-xs text-slate-400 italic">Chưa có batch nào trong cơ sở dữ liệu SQL.</p>
                  )}
                </div>
              )}
            </div>
          )}
        </main>
      </div>
    </div>
  );
};