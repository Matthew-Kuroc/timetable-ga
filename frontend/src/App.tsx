import { useState, useEffect } from 'react';
import apiClient from './api/client';

export function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [roleType, setRoleType] = useState<'ADMIN' | 'TRAINING_OFFICE' | 'LECTURER'>('ADMIN');
  const [currentUsername, setCurrentUsername] = useState('admin');
  
  // Admin & Training state
  const [adminTab, setAdminTab] = useState<'accounts' | 'csv' | 'ga' | 'approvals'>('accounts');
  const [accounts, setAccounts] = useState([
    { id: 1, username: 'admin', fullname: 'Quản trị viên Hệ thống', role: 'ADMIN', status: 'ACTIVE' },
    { id: 2, username: 'pdt', fullname: 'Phòng Đào Tạo', role: 'TRAINING_OFFICE', status: 'ACTIVE' },
    { id: 3, username: 'gv001', fullname: 'ThS. Nguyễn Văn A', role: 'LECTURER', status: 'ACTIVE' },
    { id: 4, username: 'gv002', fullname: 'ThS. Trần Văn B', role: 'LECTURER', status: 'INACTIVE' }
  ]);
  
  const [searchFilter, setSearchFilter] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [newAcc, setNewAcc] = useState({ username: '', fullname: '', role: 'LECTURER' });

  // GA & CSV Datasets state
  const [officialFiles, setOfficialFiles] = useState<any[]>([]);
  const [batches, setBatches] = useState<any[]>([]);
  const [gaConfig, setGaConfig] = useState({
    populationSize: 100,
    generations: 500,
    mutationRate: 0.05,
    crossoverRate: 0.8
  });

  // Lecturer state
  const [lecTab, setLecTab] = useState<'calendar' | 'requests'>('calendar');
  const [lecView, setLecView] = useState<'week' | 'list' | 'month' | 'day'>('week');
  const [weekOffset, setWeekOffset] = useState(4);
  const [requests, setRequests] = useState([
    { id: 'REQ-001', content: 'Đổi Lập trình Web sang T3', reason: 'Trùng lịch hội thảo', status: 'Chờ duyệt' }
  ]);
  // Hàm bóc tách trực tiếp tên/mã môn học từ dữ liệu thực tế của GA Backend
  const getBackendSubjectName = (item: any) => {
    if (!item) return 'Lớp học phần';
    // Ưu tiên các trường tên môn hoặc mã môn từ object thật của backend
    return item.course_name || item.subject_name || item.course_code || item.subject_code || item.section_code || item.name || 'Học phần GA';
  };

  const getBackendRoom = (item: any) => {
    return item?.room_code || item?.room || item?.room_name || 'A201';
  };

  const getBackendSlot = (item: any) => {
    return item?.slot_code || item?.slot || item?.time_slot || 'Tiết chuẩn';
  };
  const [isReqModalOpen, setIsReqModalOpen] = useState(false);
  const [selectedCls, setSelectedCls] = useState({ name: '', code: '', date: '', time: '', room: '' });
  const [reqReason, setReqReason] = useState('');

  // Fetch backend data
  const fetchBackendData = async () => {
    try {
      const resBatches = await apiClient.get('/batches');
      const batchData = resBatches.data;
      setBatches(Array.isArray(batchData) ? batchData : batchData.items || batchData.batches || []);

      const resFiles = await apiClient.get('/datasets/official/files');
      const fileData = resFiles.data;
      setOfficialFiles(Array.isArray(fileData) ? fileData : fileData.items || fileData.files || []);
    } catch (err) {
      console.error('Lỗi khi gọi API backend:', err);
    }
  };

  useEffect(() => {
    if (isLoggedIn) {
      fetchBackendData();
    }
  }, [isLoggedIn]);

  // Login handler
  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    const val = currentUsername.trim().toLowerCase();
    if (val === 'admin') {
      setRoleType('ADMIN');
      setAdminTab('accounts');
    } else if (val === 'pdt') {
      setRoleType('TRAINING_OFFICE');
      setAdminTab('csv');
    } else {
      setRoleType('LECTURER');
    }
    setIsLoggedIn(true);
  };

  const quickLogin = (user: string) => {
    setCurrentUsername(user);
    if (user === 'admin') {
      setRoleType('ADMIN');
      setAdminTab('accounts');
    } else if (user === 'pdt') {
      setRoleType('TRAINING_OFFICE');
      setAdminTab('csv');
    } else {
      setRoleType('LECTURER');
    }
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
  };

  // Toggle status with confirmation
  const toggleStatus = (id: number, username: string, currentStatus: string) => {
    const actionName = currentStatus === 'ACTIVE' ? 'vô hiệu hóa' : 'kích hoạt';
    if (window.confirm(`Bạn có chắc chắn muốn ${actionName} tài khoản [${username}] không?`)) {
      setAccounts(accounts.map(a => a.id === id ? { ...a, status: currentStatus === 'ACTIVE' ? 'INACTIVE' : 'ACTIVE' } : a));
    }
  };

  const saveNewUser = () => {
    if (!newAcc.username || !newAcc.fullname) {
      alert('Vui lòng nhập đầy đủ thông tin!');
      return;
    }
    setAccounts([...accounts, { id: accounts.length + 1, ...newAcc, status: 'ACTIVE' }]);
    setIsCreateModalOpen(false);
    setNewAcc({ username: '', fullname: '', role: 'LECTURER' });
    alert('Cấp tài khoản mới thành công!');
  };

  const submitRequest = () => {
    if (!reqReason.trim()) {
      alert('Vui lòng nhập lý do!');
      return;
    }
    setRequests([
      { id: `REQ-00${requests.length + 1}`, content: `Đổi ${selectedCls.name} (${selectedCls.code})`, reason: reqReason, status: 'Chờ duyệt' },
      ...requests
    ]);
    setIsReqModalOpen(false);
    setReqReason('');
    setLecTab('requests');
    alert('Gửi yêu cầu thành công!');
  };

  const filteredAccounts = accounts.filter(a => 
    (a.username.toLowerCase().includes(searchFilter.toLowerCase()) || a.fullname.toLowerCase().includes(searchFilter.toLowerCase())) &&
    (roleFilter ? a.role === roleFilter : true) &&
    (statusFilter ? a.status === statusFilter : true)
  );

  return (
    <div className="min-h-screen bg-slate-900 text-slate-800 antialiased font-['Inter',sans-serif]">
      
      {/* 1. MÀN HÌNH ĐĂNG NHẬP */}
      {!isLoggedIn && (
        <div className="min-h-screen flex items-center justify-center p-6 bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900">
          <div className="bg-white rounded-3xl shadow-2xl max-w-md w-full p-8 border border-slate-700/50">
            <div className="text-center mb-8">
              <div className="w-14 h-14 bg-indigo-600 rounded-2xl mx-auto flex items-center justify-center text-white font-bold text-2xl shadow-lg shadow-indigo-600/30 mb-4">H</div>
              <h1 className="text-2xl font-bold text-slate-900">Cổng Đào Tạo & Xếp Lịch GA</h1>
              <p className="text-xs text-slate-500 mt-1">Trường Đại học Công Thương TP.HCM (HUIT)</p>
            </div>

            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">Tên đăng nhập (Username)</label>
                <input 
                  type="text" 
                  value={currentUsername} 
                  onChange={(e) => setCurrentUsername(e.target.value)} 
                  required 
                  placeholder="admin, pdt hoặc gv001" 
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:bg-white focus:ring-2 focus:ring-indigo-600 outline-none transition"
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">Mật khẩu</label>
                <input type="password" required defaultValue="******" className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:bg-white focus:ring-2 focus:ring-indigo-600 outline-none transition" />
              </div>
              <button type="submit" className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3.5 rounded-xl shadow-lg shadow-indigo-600/30 transition text-sm">
                Đăng nhập hệ thống
              </button>
            </form>

            <div className="mt-6 pt-6 border-t border-slate-100 text-center">
              <p className="text-xs text-slate-500 mb-3">Tài khoản trải nghiệm nhanh:</p>
              <div className="flex gap-2 justify-center">
                <button type="button" onClick={() => quickLogin('admin')} className="px-3 py-1.5 bg-slate-100 hover:bg-indigo-50 text-indigo-700 font-semibold rounded-lg text-xs border">🛡️ Admin</button>
                <button type="button" onClick={() => quickLogin('pdt')} className="px-3 py-1.5 bg-slate-100 hover:bg-indigo-50 text-indigo-700 font-semibold rounded-lg text-xs border">📁 Phòng Đào Tạo</button>
                <button type="button" onClick={() => quickLogin('gv001')} className="px-3 py-1.5 bg-slate-100 hover:bg-indigo-50 text-indigo-700 font-semibold rounded-lg text-xs border">👨‍🏫 Giảng Viên</button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 2. GIAO DIỆN CHÍNH */}
      {isLoggedIn && (
        <div className="min-h-screen flex flex-col bg-slate-100">
          
          <header className="bg-indigo-900 text-white shadow-md z-20">
            <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-indigo-600 flex items-center justify-center font-bold text-lg">H</div>
                <div>
                  <h1 className="font-bold text-base">
                    {roleType === 'ADMIN' ? 'Cổng Quản Trị Hệ Thống (Admin)' : roleType === 'TRAINING_OFFICE' ? 'Cổng Quản Lý Đào Tạo & GA' : 'Cổng Thông Tin Giảng Viên'}
                  </h1>
                  <p className="text-xs text-indigo-300">Đại học Công Thương TP.HCM (HUIT)</p>
                </div>
              </div>

              <div className="flex items-center gap-4">
                <div className="bg-indigo-800/80 px-3 py-1.5 rounded-lg border border-indigo-700 text-xs font-medium flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                  <span>Role: {roleType} ({currentUsername})</span>
                </div>
                <button onClick={handleLogout} className="bg-rose-600 hover:bg-rose-700 text-white text-xs font-semibold px-4 py-2 rounded-lg transition shadow-sm">
                  Đăng xuất
                </button>
              </div>
            </div>
          </header>

          <div className="flex-1 flex max-w-7xl w-full mx-auto">
            
            {/* Sidebar */}
            <aside className="w-72 bg-white border-r border-slate-200 p-6 flex flex-col justify-between shadow-xs">
              <div>
                <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Menu Điều Hướng</p>
                
                {roleType === 'ADMIN' && (
                  <nav className="space-y-1.5">
                    <button onClick={() => setAdminTab('accounts')} className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-semibold transition text-left ${adminTab === 'accounts' ? 'bg-indigo-50 text-indigo-700' : 'hover:bg-slate-50 text-slate-600'}`}>👥 Quản lý tài khoản</button>
                  </nav>
                )}

                {roleType === 'TRAINING_OFFICE' && (
                  <nav className="space-y-1.5">
                    <button onClick={() => setAdminTab('csv')} className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-semibold transition text-left ${adminTab === 'csv' ? 'bg-indigo-50 text-indigo-700' : 'hover:bg-slate-50 text-slate-600'}`}>📁 Quản lý dữ liệu CSV</button>
                    <button onClick={() => setAdminTab('ga')} className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-semibold transition text-left ${adminTab === 'ga' ? 'bg-indigo-50 text-indigo-700' : 'hover:bg-slate-50 text-slate-600'}`}>⚙️ Cấu hình & Chạy GA</button>
                    <button onClick={() => setAdminTab('approvals')} className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-semibold transition text-left ${adminTab === 'approvals' ? 'bg-indigo-50 text-indigo-700' : 'hover:bg-slate-50 text-slate-600'}`}>✅ Phê duyệt đổi lịch</button>
                  </nav>
                )}

                {roleType === 'LECTURER' && (
                  <nav className="space-y-1.5">
                    <button onClick={() => setLecTab('calendar')} className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-semibold transition text-left ${lecTab === 'calendar' ? 'bg-indigo-50 text-indigo-700' : 'hover:bg-slate-50 text-slate-600'}`}>📅 Lịch Giảng Dạy</button>
                    <button onClick={() => setLecTab('requests')} className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-semibold transition text-left ${lecTab === 'requests' ? 'bg-indigo-50 text-indigo-700' : 'hover:bg-slate-50 text-slate-600'}`}>🕒 Theo dõi Request</button>
                    
                    <div className="pt-4 mt-4 border-t border-slate-100 space-y-2">
                      <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">Công cụ xuất báo cáo</p>
                      <button onClick={() => window.print()} className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold transition shadow-sm">🖨️ In lịch giảng dạy</button>
                      <button onClick={() => alert('Đang xuất file Excel...')} className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold transition shadow-sm">📥 Xuất file Excel</button>
                    </div>
                  </nav>
                )}
              </div>
              <div className="pt-6 border-t border-slate-100">
                <div className="bg-slate-50 p-3 rounded-xl border text-center text-xs text-slate-600 font-semibold">Đồ án Tốt nghiệp 2026</div>
              </div>
            </aside>

            {/* Main Workspace */}
            <main className="flex-1 p-8 overflow-y-auto">
              
              {/* ADMIN & TRAINING WORKSPACE */}
              {(roleType === 'ADMIN' || roleType === 'TRAINING_OFFICE') && (
                <div className="space-y-6">
                  
                  {/* 1. QUẢN LÝ TÀI KHOẢN (Chỉ dành cho ADMIN) */}
                  {roleType === 'ADMIN' && adminTab === 'accounts' && (
                    <div className="space-y-6">
                      <div className="bg-white p-6 rounded-2xl border shadow-xs flex justify-between items-center">
                        <div>
                          <h2 className="text-xl font-bold text-slate-800">Quản lý Tài khoản Hệ thống</h2>
                          <p className="text-xs text-slate-500 mt-0.5">Tìm kiếm, lọc, cấp tài khoản và kích hoạt/vô hiệu hóa người dùng.</p>
                        </div>
                        <button onClick={() => setIsCreateModalOpen(true)} className="bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold px-4 py-2.5 rounded-xl shadow transition">+ Cấp tài khoản mới</button>
                      </div>

                      <div className="bg-white p-4 rounded-2xl border shadow-xs flex gap-3">
                        <input 
                          type="text" 
                          value={searchFilter} 
                          onChange={(e) => setSearchFilter(e.target.value)} 
                          placeholder="🔍 Tìm kiếm theo username hoặc họ tên..." 
                          className="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-xs outline-none focus:bg-white focus:ring-2 focus:ring-indigo-600"
                        />
                        <select value={roleFilter} onChange={(e) => setRoleFilter(e.target.value)} className="bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-xs outline-none font-medium">
                          <option value="">Tất cả Role</option>
                          <option value="ADMIN">ADMIN</option>
                          <option value="TRAINING_OFFICE">TRAINING_OFFICE</option>
                          <option value="LECTURER">LECTURER</option>
                        </select>
                        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-xs outline-none font-medium">
                          <option value="">Tất cả trạng thái</option>
                          <option value="ACTIVE">ACTIVE</option>
                          <option value="INACTIVE">INACTIVE</option>
                        </select>
                      </div>

                      <div className="bg-white rounded-2xl border shadow-xs overflow-hidden">
                        <table className="w-full text-left text-sm">
                          <thead className="bg-slate-50 text-slate-400 uppercase text-[10px] font-bold border-b">
                            <tr><th className="p-4">Username</th><th className="p-4">Họ tên</th><th className="p-4">Role</th><th className="p-4">Trạng thái</th><th className="p-4 text-right">Thao tác</th></tr>
                          </thead>
                          <tbody className="divide-y text-sm">
                            {filteredAccounts.map(acc => (
                              <tr key={acc.id} className="hover:bg-slate-50">
                                <td className="p-4 font-bold text-indigo-600">{acc.username}</td>
                                <td className="p-4">{acc.fullname}</td>
                                <td className="p-4"><span className="bg-slate-100 text-xs px-2.5 py-1 rounded-lg font-semibold">{acc.role}</span></td>
                                <td className="p-4"><span className={`text-xs px-2.5 py-1 rounded-full font-semibold ${acc.status === 'ACTIVE' ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'}`}>{acc.status}</span></td>
                                <td className="p-4 text-right">
                                  <button onClick={() => toggleStatus(acc.id, acc.username, acc.status)} className={`text-xs font-semibold px-3 py-1.5 rounded-lg ${acc.status === 'ACTIVE' ? 'bg-rose-50 text-rose-600' : 'bg-emerald-50 text-emerald-600'}`}>
                                    {acc.status === 'ACTIVE' ? 'Vô hiệu hóa' : 'Kích hoạt'}
                                  </button>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}

                 {/* HIỂN THỊ DANH SÁCH TỆP CSV GỌN GÀNG, ĐẸP MẮT */}
                  {adminTab === 'csv' && (
                    <div className="bg-white p-8 rounded-2xl border shadow-xs space-y-4">
                      <div className="flex justify-between items-center">
                        <div>
                          <h3 className="font-bold text-lg text-slate-800">📁 Quản lý dữ liệu CSV đầu vào (Datasets)</h3>
                          <p className="text-xs text-slate-500 mt-0.5">Danh sách các tệp dữ liệu đã được đồng bộ từ Backend Database.</p>
                        </div>
                        <button onClick={fetchBackendData} className="bg-indigo-50 hover:bg-indigo-100 text-indigo-700 text-xs font-bold px-3 py-2 rounded-xl transition">🔄 Tải lại dữ liệu</button>
                      </div>

                      <div className="space-y-3 pt-2">
                        {officialFiles.length > 0 ? (
                          officialFiles.map((item, idx) => {
                            const fileName = typeof item === 'string' ? item : item.file || item.file_name || `Dataset_${idx}`;
                            const headers = item.headers ? item.headers.join(', ') : '';
                            const rowCount = item.row_count !== undefined ? `(${item.row_count} dòng)` : '';

                            return (
                              <div key={idx} className="p-4 bg-slate-50 border border-slate-200 rounded-2xl flex items-center justify-between transition hover:border-indigo-200">
                                <div className="space-y-1">
                                  <div className="flex items-center gap-2">
                                    <span className="font-bold text-sm text-indigo-900">📄 {fileName}</span>
                                    {rowCount && <span className="text-[10px] bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full font-semibold">{rowCount}</span>}
                                  </div>
                                  {headers && <p className="text-[11px] text-slate-500 truncate max-w-xl"><strong>Cột dữ liệu:</strong> {headers}</p>}
                                </div>
                                <span className="text-xs bg-emerald-100 text-emerald-800 px-3 py-1 rounded-full font-bold">Sẵn sàng</span>
                              </div>
                            );
                          })
                        ) : (
                          <p className="text-xs text-slate-400 italic">Không có tệp dữ liệu nào trong hệ thống.</p>
                        )}
                      </div>
                    </div>
                  )}

                 {/* HIỂN THỊ DANH SÁCH BATCH GỌN GÀNG TỪ BACKEND */}
                  {roleType === 'TRAINING_OFFICE' && adminTab === 'ga' && (
                    <div className="bg-white p-8 rounded-2xl border shadow-xs space-y-6">
                      <div className="flex justify-between items-center">
                        <div>
                          <h3 className="font-bold text-lg text-slate-800">⚙️ Cấu hình thông số và Chạy thuật toán GA</h3>
                          <p className="text-xs text-slate-500">Tùy chỉnh các thông số thuật toán di truyền để tối ưu thời khóa biểu.</p>
                        </div>
                        <button 
                          onClick={async () => {
                            try {
                              alert('Đã gửi yêu cầu chạy GA. Thuật toán đang tính toán trên server, vui lòng đợi trong giây lát...');
                              const res = await apiClient.post('/ga/runs/preview', {
                                batch_code: 'BATCH-20260809-184731-D2A2D3',
                                population_size: 20,
                                generations: 50,
                                mutation_rate: gaConfig.mutationRate,
                                crossover_rate: gaConfig.crossoverRate
                              }, {
                                timeout: 60000 
                              });
                              console.log('Kết quả GA:', res.data);
                              if (res.data.occurrences) {
                                localStorage.setItem('lecturer_timetable', JSON.stringify(res.data.occurrences));
                              }
                              alert('Chạy thuật toán GA thành công!');
                              fetchBackendData();
                            } catch (err: any) {
                              console.error('Chi tiết lỗi:', err);
                              alert('Lỗi: ' + (err.response?.data?.detail || err.message));
                            }
                          }} 
                          className="bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold px-5 py-2.5 rounded-xl shadow transition"
                        >
                          ⚡ Chạy thuật toán GA
                        </button>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-1.5">
                          <label className="block text-xs font-bold text-slate-700">Kích thước quần thể (Population Size)</label>
                          <input type="number" value={gaConfig.populationSize} onChange={e => setGaConfig({...gaConfig, populationSize: Number(e.target.value)})} className="w-full bg-slate-50 border rounded-xl px-3 py-2 text-xs outline-none" />
                        </div>
                        <div className="space-y-1.5">
                          <label className="block text-xs font-bold text-slate-700">Số thế hệ (Generations)</label>
                          <input type="number" value={gaConfig.generations} onChange={e => setGaConfig({...gaConfig, generations: Number(e.target.value)})} className="w-full bg-slate-50 border rounded-xl px-3 py-2 text-xs outline-none" />
                        </div>
                        <div className="space-y-1.5">
                          <label className="block text-xs font-bold text-slate-700">Tỷ lệ đột biến (Mutation Rate)</label>
                          <input type="number" step="0.01" value={gaConfig.mutationRate} onChange={e => setGaConfig({...gaConfig, mutationRate: Number(e.target.value)})} className="w-full bg-slate-50 border rounded-xl px-3 py-2 text-xs outline-none" />
                        </div>
                        <div className="space-y-1.5">
                          <label className="block text-xs font-bold text-slate-700">Tỷ lệ lai ghép (Crossover Rate)</label>
                          <input type="number" step="0.01" value={gaConfig.crossoverRate} onChange={e => setGaConfig({...gaConfig, crossoverRate: Number(e.target.value)})} className="w-full bg-slate-50 border rounded-xl px-3 py-2 text-xs outline-none" />
                        </div>
                      </div>

                      <div className="p-5 bg-slate-50 border rounded-2xl space-y-3">
                        <h4 className="font-bold text-xs text-slate-700 uppercase">📦 Các Batch hiện có ({batches.length})</h4>
                        {batches.length > 0 ? (
                          batches.map((b, i) => {
                            const code = typeof b === 'string' ? b : b.batch_code || 'BATCH_UNKNOWN';
                            const name = typeof b === 'object' && b.display_name ? b.display_name : 'Bộ dữ liệu chính thức';
                            const time = typeof b === 'object' && b.created_at ? new Date(b.created_at).toLocaleString() : '';

                            return (
                              <div key={i} className="p-3 bg-white border border-slate-200 rounded-xl flex items-center justify-between text-xs">
                                <div>
                                  <span className="font-bold text-indigo-900">📦 {code}</span>
                                  <p className="text-slate-500 text-[11px] mt-0.5">{name} {time && `— ${time}`}</p>
                                </div>
                                <span className="text-[10px] bg-indigo-100 text-indigo-800 px-2.5 py-1 rounded-lg font-bold">Đang chọn</span>
                              </div>
                            );
                          })
                        ) : (
                          <div className="text-xs text-slate-500 italic">Chưa có batch nào trong hệ thống.</div>
                        )}
                      </div>
                    </div>
                  )}

                  {roleType === 'TRAINING_OFFICE' && adminTab === 'approvals' && (
                    <div className="bg-white p-8 rounded-2xl border shadow-xs text-center">
                      <h3 className="font-bold text-lg text-slate-800">✅ Phê duyệt yêu cầu đổi lịch</h3>
                      <p className="text-xs text-slate-500 mt-1">Chưa có yêu cầu đổi lịch nào cần xét duyệt.</p>
                    </div>
                  )}
                </div>
              )}

              {/* LECTURER WORKSPACE */}
              {roleType === 'LECTURER' && (
                <div className="space-y-6">
                  {lecTab === 'calendar' ? (
                    <div className="space-y-6">
                      <div className="flex justify-between items-center bg-white p-5 rounded-2xl border shadow-xs">
                        <div>
                          <h2 className="text-xl font-bold text-slate-800">Lịch Giảng Dạy Cá Nhân</h2>
                          <p className="text-xs text-slate-500 mt-0.5">Chỉ hiển thị dữ liệu của giảng viên đang đăng nhập.</p>
                        </div>
                        <div className="flex bg-slate-100 p-1.5 rounded-2xl border gap-1">
                          <button onClick={() => setLecView('list')} className={`px-4 py-2 text-xs font-bold rounded-xl transition ${lecView === 'list' ? 'bg-indigo-600 text-white shadow' : 'text-slate-600'}`}>Danh Sách</button>
                          <button onClick={() => setLecView('month')} className={`px-4 py-2 text-xs font-bold rounded-xl transition ${lecView === 'month' ? 'bg-indigo-600 text-white shadow' : 'text-slate-600'}`}>Theo Tháng</button>
                          <button onClick={() => setLecView('week')} className={`px-4 py-2 text-xs font-bold rounded-xl transition ${lecView === 'week' ? 'bg-indigo-600 text-white shadow' : 'text-slate-600'}`}>Theo Tuần</button>
                          <button onClick={() => setLecView('day')} className={`px-4 py-2 text-xs font-bold rounded-xl transition ${lecView === 'day' ? 'bg-indigo-600 text-white shadow' : 'text-slate-600'}`}>Theo Ngày</button>
                        </div>
                      </div>

                     {lecView === 'week' && (() => {
                        const savedData = localStorage.getItem('lecturer_timetable');
                        const allTimetable = savedData ? JSON.parse(savedData) : [];

                        return (
                          <div className="space-y-4">
                            <div className="flex justify-between items-center bg-white p-4 rounded-2xl border shadow-xs">
                              <div>
                                <h3 className="text-base font-bold text-slate-800">Thời khóa biểu Tuần hệ thống GA</h3>
                                <p className="text-xs text-slate-500">Tổng số buổi phân công: {allTimetable.length} buổi</p>
                              </div>
                              <div className="flex items-center gap-2">
                                <button onClick={() => setWeekOffset(p => Math.max(1, p - 1))} className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-xs font-bold rounded-lg">&lt; Tuần trước</button>
                                <button onClick={() => setWeekOffset(4)} className="px-3 py-1.5 bg-indigo-50 text-indigo-700 text-xs font-bold rounded-lg">Tuần hiện tại</button>
                                <button onClick={() => setWeekOffset(p => p + 1)} className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-xs font-bold rounded-lg">Tuần sau &gt;</button>
                              </div>
                            </div>

                            <div className="grid grid-cols-7 gap-3">
                              {['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'Chủ Nhật'].map((day, idx) => {
                                // Lọc chính xác các lớp theo đúng ngày trong mảng dữ liệu thật
                                const targetDayIndex = idx + 2; // Chuẩn thứ trong tuần
                                const dayClasses = allTimetable.filter((item: any) => {
                                  if (!item.date) return idx === 0;
                                  const itemDate = new Date(item.date);
                                  return itemDate.getDay() === (targetDayIndex === 8 ? 0 : targetDayIndex);
                                }).slice(0, 4);

                                return (
                                  <div key={idx} className="bg-white border rounded-xl p-2.5 min-h-[500px] flex flex-col justify-between shadow-xs">
                                    <div className="text-center pb-2 border-b mb-2">
                                      <span className="text-[10px] font-bold text-slate-400 uppercase">{day}</span>
                                    </div>
                                    <div className="flex-1 flex flex-col gap-2 overflow-y-auto max-h-[450px]">
                                      {dayClasses.length > 0 ? (
                                        dayClasses.map((cls: any, cIdx: number) => (
                                          <div 
                                            key={cIdx} 
                                            onClick={() => { 
                                              setSelectedCls({ 
                                                name: cls.course_name || cls.course_code || 'Lớp GA', 
                                                code: cls.course_code || 'GA', 
                                                date: cls.date || day, 
                                                time: cls.slot_code || cls.slot || 'Tiết chuẩn', 
                                                room: cls.room_code || cls.room || 'A201' 
                                              }); 
                                              setIsReqModalOpen(true); 
                                            }} 
                                            className="bg-indigo-50 border p-2 rounded-lg cursor-pointer hover:border-indigo-300 transition text-left"
                                          >
                                            <span className="text-[9px] bg-indigo-600 text-white px-1 rounded font-bold">{cls.slot_code || 'Slot'}</span>
                                            <p className="font-bold text-[11px] text-indigo-900 mt-1 truncate">{cls.course_code || cls.course_name || 'Môn học'}</p>
                                            <p className="text-[10px] text-slate-500">Phòng: {cls.room_code || cls.room || 'A201'}</p>
                                          </div>
                                        ))
                                      ) : (
                                        <div className="text-center py-4 text-slate-300 text-[10px] bg-slate-50/50 rounded-lg">Trống</div>
                                      )}
                                    </div>
                                  </div>
                                );
                              })}
                            </div>
                          </div>
                        );
                      })()}

                      {lecView === 'day' && (() => {
                        const savedData = localStorage.getItem('lecturer_timetable');
                        const allTimetable = savedData ? JSON.parse(savedData) : [];
                        const dayClasses = allTimetable.slice(0, 10); // Hiển thị danh sách các buổi học chi tiết

                        return (
                          <div className="space-y-4">
                            <div className="bg-white p-5 rounded-2xl border shadow-xs flex justify-between items-center">
                              <h3 className="font-bold text-slate-800 text-sm">Chi tiết lịch trình theo ngày phân công từ GA</h3>
                              <input type="date" defaultValue="2026-09-09" className="border text-xs px-3 py-1.5 rounded-lg outline-none" />
                            </div>
                            
                            {dayClasses.length > 0 ? (
                              dayClasses.map((item: any, idx: number) => (
                                <div key={idx} className="bg-white p-5 rounded-2xl border shadow-xs flex items-center justify-between">
                                  <div>
                                    <span className="bg-indigo-100 text-indigo-700 text-xs px-2.5 py-1 rounded-lg font-bold">{item.slot_code || item.slot || 'Tiết chuẩn'}</span>
                                    <h4 className="font-bold text-slate-900 mt-2">{item.course_code || item.course_name || 'Môn học phần'}</h4>
                                    <p className="text-xs text-slate-500 mt-0.5">Phòng: {item.room_code || item.room || 'A201'} — Ngày: {item.date || '2026-09-09'}</p>
                                  </div>
                                  <button 
                                    onClick={() => { 
                                      setSelectedCls({ 
                                        name: item.course_name || 'Lớp học phần GA', 
                                        code: item.course_code || 'GA', 
                                        date: item.date || '2026-09-09', 
                                        time: item.slot_code || 'Tiết chuẩn', 
                                        room: item.room_code || 'A201' 
                                      }); 
                                      setIsReqModalOpen(true); 
                                    }} 
                                    className="bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold px-4 py-2.5 rounded-xl shadow transition"
                                  >
                                    Gửi yêu cầu đổi lịch
                                  </button>
                                </div>
                              ))
                            ) : (
                              <div className="bg-white p-8 rounded-2xl border text-center text-xs text-slate-400 italic">
                                Không có lớp học trong ngày này.
                              </div>
                            )}
                          </div>
                        );
                      })()}

                      {lecView === 'month' && (() => {
                        const savedData = localStorage.getItem('lecturer_timetable');
                        const allTimetable = savedData ? JSON.parse(savedData) : [];

                        return (
                          <div className="bg-white p-8 rounded-2xl border shadow-xs space-y-4 text-center">
                            <h3 className="font-bold text-slate-800 text-lg mb-1">Lịch biểu Tổng quan Tháng 09/2026</h3>
                            <p className="text-xs text-slate-500">Hệ thống GA đã phân bổ tổng cộng <strong className="text-indigo-600">{allTimetable.length} buổi học</strong> trong toàn bộ học kỳ.</p>
                            <div className="p-4 bg-slate-50 rounded-2xl border text-xs text-slate-600">
                              💡 Bạn có thể chuyển sang chế độ xem <strong>Danh Sách</strong> hoặc <strong>Theo Tuần</strong> để xem chi tiết từng phòng học, tiết học và thực hiện thao tác đổi lịch.
                            </div>
                          </div>
                        );
                      })()}

                      {lecView === 'list' && (() => {
                        const savedData = localStorage.getItem('lecturer_timetable');
                        const timetableList = savedData ? JSON.parse(savedData) : [];

                        return (
                          <div className="bg-white rounded-2xl border shadow-xs overflow-hidden">
                            <div className="p-4 border-b bg-slate-50 font-bold text-xs text-slate-700 uppercase flex justify-between items-center">
                              <span>Danh sách thời khóa biểu GA ({timetableList.length} buổi)</span>
                              <button onClick={() => window.location.reload()} className="text-[10px] bg-indigo-50 text-indigo-700 px-3 py-1.5 rounded-lg font-bold">🔄 Làm mới trang</button>
                            </div>
                            <table className="w-full text-left text-sm">
                              <thead className="bg-slate-50 text-slate-400 uppercase text-[10px] font-bold border-b">
                                <tr>
                                  <th className="p-4">Thứ / Ngày</th>
                                  <th className="p-4">Tiết / Slot</th>
                                  <th className="p-4">Môn học / Lớp</th>
                                  <th className="p-4">Phòng</th>
                                  <th className="p-4 text-center">Trạng thái</th>
                                  <th className="p-4 text-right">Thao tác</th>
                                </tr>
                              </thead>
                              <tbody className="divide-y text-sm">
                                {timetableList.length > 0 ? (
                                  timetableList.map((item: any, idx: number) => (
                                    <tr key={idx} className="hover:bg-slate-50">
                                      <td className="p-4 font-semibold text-xs">{item.date || 'Thứ 2 (03/09/2026)'}</td>
                                      <td className="p-4 text-xs">{item.slot_code || item.slot || 'Tiết 1-3'}</td>
                                      <td className="p-4 font-bold text-indigo-700 text-xs">
                                      {item.course_name ? `${item.course_name} (${item.course_code})` : (item.course_code || item.section_code || 'Lớp học phần GA')}                                      </td>
                                      <td className="p-4 text-xs">{item.room_code || item.room || 'A303'}</td>
                                      <td className="p-4 text-center">
                                        <span className="bg-emerald-100 text-emerald-800 text-[10px] px-2.5 py-1 rounded-full font-bold">Đã xếp</span>
                                      </td>
                                      <td className="p-4 text-right">
                                        <button 
                                          onClick={() => {
                                            setSelectedCls({
                                              name: item.course_name || 'Lớp học phần GA',
                                              code: item.course_code || 'GA_01',
                                              date: item.date || 'Thứ 2 (03/09)',
                                              time: item.slot_code || 'Tiết 1-3',
                                              room: item.room_code || 'A303'
                                            });
                                            setIsReqModalOpen(true);
                                          }}
                                          className="text-[10px] bg-indigo-600 hover:bg-indigo-700 text-white font-bold px-3 py-1.5 rounded-lg shadow transition"
                                        >
                                          Đổi lịch
                                        </button>
                                      </td>
                                    </tr>
                                  ))
                                ) : (
                                  <tr>
                                    <td colSpan={6} className="p-8 text-center text-xs text-slate-400 italic">
                                      Chưa có dữ liệu lịch. Vui lòng sang tài khoản <strong>pdt</strong> bấm <strong>"Chạy thuật toán GA"</strong> trước!
                                    </td>
                                  </tr>
                                )}
                              </tbody>
                            </table>
                          </div>
                        );
                      })()}
                    </div>
                  ) : (
                    <div className="bg-white rounded-2xl border shadow-xs overflow-hidden">
                      <div className="p-5 border-b"><h3 className="font-bold text-slate-800">Yêu cầu thay đổi lịch của bạn</h3></div>
                      <table className="w-full text-left text-sm">
                        <thead className="bg-slate-50 text-slate-400 uppercase text-[10px] font-bold border-b">
                          <tr><th className="p-4">Mã</th><th className="p-4">Nội dung đề xuất</th><th className="p-4">Lý do</th><th className="p-4">Trạng thái</th></tr>
                        </thead>
                        <tbody className="divide-y text-sm">
                          {requests.map((req, i) => (
                            <tr key={i}>
                              <td className="p-4 font-bold text-indigo-600">{req.id}</td>
                              <td className="p-4">{req.content}</td>
                              <td className="p-4 text-slate-500">{req.reason}</td>
                              <td className="p-4"><span className="bg-amber-100 text-amber-800 text-xs px-2.5 py-1 rounded-full font-semibold">{req.status}</span></td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              )}

            </main>
          </div>
        </div>
      )}

      {/* Modal Cấp tài khoản mới */}
      {isCreateModalOpen && (
        <div className="fixed inset-0 bg-slate-900/60 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-3xl max-w-md w-full p-6 space-y-4">
            <div className="flex justify-between items-center border-b pb-3">
              <h3 className="font-bold text-base">Cấp tài khoản mới</h3>
              <button onClick={() => setIsCreateModalOpen(false)}>✕</button>
            </div>
            <input type="text" value={newAcc.username} onChange={e => setNewAcc({...newAcc, username: e.target.value})} placeholder="Username (vd: gv002)" className="w-full bg-slate-50 border rounded-xl px-3 py-2 text-xs outline-none" />
            <input type="text" value={newAcc.fullname} onChange={e => setNewAcc({...newAcc, fullname: e.target.value})} placeholder="Họ và tên" className="w-full bg-slate-50 border rounded-xl px-3 py-2 text-xs outline-none" />
            <select value={newAcc.role} onChange={e => setNewAcc({...newAcc, role: e.target.value})} className="w-full bg-slate-50 border rounded-xl px-3 py-2 text-xs outline-none">
              <option value="LECTURER">LECTURER</option>
              <option value="TRAINING_OFFICE">TRAINING_OFFICE</option>
              <option value="ADMIN">ADMIN</option>
            </select>
            <button onClick={saveNewUser} className="w-full bg-indigo-600 text-white text-xs font-bold py-3 rounded-xl">Lưu tài khoản</button>
          </div>
        </div>
      )}

      {/* Modal Tạo Request */}
      {isReqModalOpen && (
        <div className="fixed inset-0 bg-slate-900/60 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-3xl max-w-md w-full p-6 space-y-4">
            <div className="flex justify-between items-center border-b pb-3">
              <h3 className="font-bold text-base">Tạo yêu cầu đổi lịch</h3>
              <button onClick={() => setIsReqModalOpen(false)}>✕</button>
            </div>
            <div className="bg-slate-50 p-3 rounded-xl text-xs space-y-1">
              <p><strong>Môn:</strong> {selectedCls.name} ({selectedCls.code})</p>
              <p><strong>Thời gian:</strong> {selectedCls.date} - {selectedCls.time} (Phòng {selectedCls.room})</p>
            </div>
            <input 
              type="text" 
              value={reqReason} 
              onChange={e => setReqReason(e.target.value)} 
              placeholder="Nhập lý do đổi lịch..." 
              className="w-full bg-slate-50 border rounded-xl px-3 py-2 text-xs outline-none focus:ring-2 focus:ring-indigo-600"
            />
            <button onClick={submitRequest} className="w-full bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold py-3 rounded-xl shadow">
              Gửi yêu cầu
            </button>
          </div>
        </div>
      )}

    </div>
  );
}

export default App;