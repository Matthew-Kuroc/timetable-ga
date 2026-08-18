import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../../api/client';

export const LecturerPage = () => {
  const [activeTab, setActiveTab] = useState<'calendar' | 'requests'>('calendar');
  const [activeView, setActiveView] = useState<'week' | 'list' | 'month' | 'day'>('week');
  const [currentWeekOffset, setCurrentWeekOffset] = useState(4);
  
  // State lưu thời khóa biểu thực tế từ Backend GA
  const [timetables, setTimetables] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const currentLecturer = localStorage.getItem('username') || 'gv001';

  const [requests, setRequests] = useState([
    { id: 'REQ-001', content: 'Đổi Lập trình Web sang T3', reason: 'Trùng lịch hội thảo', status: 'Chờ duyệt' }
  ]);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedClass, setSelectedClass] = useState({ name: '', code: '', date: '', time: '', room: '' });
  const [reasonText, setReasonText] = useState('');

  const navigate = useNavigate();
const fetchLecturerSchedule = async () => {
    try {
      setLoading(true);
      setError('');
      const res = await apiClient.get('/ga/official-timetables');
      console.log("Dữ liệu trả về từ API /ga/official-timetables:", res.data); // 👈 Bật F12 Console để xem cấu trúc thật
      
      const data = res.data;
      // Tự động quét mọi trường hợp cấu trúc trả về từ backend
      const items = Array.isArray(data) ? data : data.items || data.timetables || data.data || [];
      setTimetables(items);
    } catch (err) {
      console.error('Lỗi khi tải lịch từ GA:', err);
      setError('Không thể kết nối hoặc tải dữ liệu lịch từ Backend.');
    } finally {
      setLoading(false);
    }
  };
  useEffect(() => {
    fetchLecturerSchedule();
  }, []);

  const handleLogout = () => {
    localStorage.clear();
    navigate('/login');
  };

  const openRequestModal = (name: string, code: string, date: string, time: string, room: string) => {
    setSelectedClass({ name, code, date, time, room });
    setIsModalOpen(true);
  };

  const submitLecRequest = () => {
    if (!reasonText.trim()) {
      alert('Vui lòng nhập lý do đổi lịch!');
      return;
    }
    const newReq = {
      id: `REQ-00${requests.length + 1}`,
      content: `Đổi ${selectedClass.name} (${selectedClass.code})`,
      reason: reasonText,
      status: 'Chờ duyệt'
    };
    setRequests([newReq, ...requests]);
    setIsModalOpen(false);
    setReasonText('');
    setActiveTab('requests');
    alert('Gửi yêu cầu đổi lịch thành công!');
  };

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col">
      {/* Header */}
      <header className="bg-indigo-900 text-white shadow-md z-20">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-indigo-600 flex items-center justify-center font-bold text-lg">H</div>
            <div>
              <h1 className="font-bold text-base">Cổng Thông Tin Giảng Viên</h1>
              <p className="text-xs text-indigo-300">Đại học Công Thương TP.HCM (HUIT)</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="bg-indigo-800/80 px-3 py-1.5 rounded-lg border border-indigo-700 text-xs font-medium flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
              <span>Role: LECTURER ({currentLecturer})</span>
            </div>
            <button onClick={handleLogout} className="bg-rose-600 hover:bg-rose-700 text-white text-xs font-semibold px-4 py-2 rounded-lg transition shadow-sm">
              Đăng xuất
            </button>
          </div>
        </div>
      </header>

      {/* Main Body */}
      <div className="flex flex-1 max-w-7xl w-full mx-auto">
        {/* Sidebar */}
        <aside className="w-72 bg-white border-r border-slate-200 p-6 flex flex-col justify-between shadow-xs">
          <div className="space-y-1.5">
            <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Menu Giảng Viên</p>
            <button onClick={() => setActiveTab('calendar')} className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-semibold transition text-left ${activeTab === 'calendar' ? 'bg-indigo-50 text-indigo-700' : 'hover:bg-slate-50 text-slate-600'}`}>
              📅 Lịch Giảng Dạy
            </button>
            <button onClick={() => setActiveTab('requests')} className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-semibold transition text-left ${activeTab === 'requests' ? 'bg-indigo-50 text-indigo-700' : 'hover:bg-slate-50 text-slate-600'}`}>
              🕒 Theo dõi Request
            </button>

            <div className="pt-4 mt-4 border-t border-slate-100 space-y-2">
              <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">Công cụ xuất báo cáo</p>
              <button onClick={() => window.print()} className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold transition shadow-sm">🖨️ In lịch giảng dạy</button>
              <button onClick={() => alert('Đang xuất file Excel...')} className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold transition shadow-sm">📥 Xuất file Excel</button>
            </div>
          </div>
          <div className="pt-6 border-t border-slate-100">
            <div className="bg-slate-50 p-3 rounded-xl border text-center text-xs text-slate-600 font-semibold">Đồ án Tốt nghiệp 2026</div>
          </div>
        </aside>

        {/* Content Workspace */}
        <main className="flex-1 p-8 overflow-y-auto">
          {error && <div className="mb-4 bg-rose-50 border border-rose-200 text-rose-700 text-xs p-4 rounded-xl">{error}</div>}

          {activeTab === 'calendar' ? (
            <div className="space-y-6">
              {/* Top Bar Views */}
              <div className="flex justify-between items-center bg-white p-5 rounded-2xl border shadow-xs">
                <div>
                  <h2 className="text-xl font-bold text-slate-800">Lịch Giảng Dạy Cá Nhân (GA Engine)</h2>
                  <p className="text-xs text-slate-500 mt-0.5">Dữ liệu được lấy trực tiếp từ hệ thống xếp lịch GA của Backend.</p>
                </div>
                <div className="flex bg-slate-100 p-1.5 rounded-2xl border gap-1">
                  <button onClick={() => setActiveView('list')} className={`px-4 py-2 text-xs font-bold rounded-xl transition ${activeView === 'list' ? 'bg-indigo-600 text-white shadow' : 'text-slate-600'}`}>Danh Sách</button>
                  <button onClick={() => setActiveView('month')} className={`px-4 py-2 text-xs font-bold rounded-xl transition ${activeView === 'month' ? 'bg-indigo-600 text-white shadow' : 'text-slate-600'}`}>Theo Tháng</button>
                  <button onClick={() => setActiveView('week')} className={`px-4 py-2 text-xs font-bold rounded-xl transition ${activeView === 'week' ? 'bg-indigo-600 text-white shadow' : 'text-slate-600'}`}>Theo Tuần</button>
                  <button onClick={() => setActiveView('day')} className={`px-4 py-2 text-xs font-bold rounded-xl transition ${activeView === 'day' ? 'bg-indigo-600 text-white shadow' : 'text-slate-600'}`}>Theo Ngày</button>
                </div>
              </div>

              {loading ? (
                <div className="bg-white p-8 rounded-2xl border text-center text-xs text-slate-500">Đang đồng bộ lịch từ thuật toán GA...</div>
              ) : (
                <>
                 {lecView === 'list' && (() => {
                        // Lấy dữ liệu lịch GA đã lưu từ localStorage sau khi chạy preview thành công
                        const savedTimetable = localStorage.getItem('lecturer_timetable');
                        const lecturerList = savedTimetable ? JSON.parse(savedTimetable) : [];

                        return (
                          <div className="bg-white rounded-2xl border shadow-xs overflow-hidden">
                            <div className="p-4 border-b bg-slate-50 font-bold text-xs text-slate-700 uppercase flex justify-between items-center">
                              <span>Danh sách lịch phân công từ GA Engine ({lecturerList.length} buổi học)</span>
                              <button onClick={() => window.location.reload()} className="text-[10px] bg-indigo-50 text-indigo-700 px-2.5 py-1 rounded-lg">🔄 Làm mới</button>
                            </div>
                            <div className="divide-y text-sm max-h-[500px] overflow-y-auto">
                              {lecturerList.length > 0 ? (
                                lecturerList.map((item: any, idx: number) => (
                                  <div key={idx} className="p-4 hover:bg-slate-50 flex items-center justify-between text-xs font-mono text-slate-700">
                                    <div>
                                      <span className="font-bold text-indigo-900">📚 Môn: {item.course_code || item.section_code || `Buổi #${idx + 1}`}</span>
                                      <p className="text-slate-500 mt-0.5">Phòng: {item.room_code || item.room || 'Chưa xếp'} — Slot: {item.slot_code || item.slot || 'Tiết chuẩn'}</p>
                                    </div>
                                    <div className="flex items-center gap-2">
                                      <span className="bg-emerald-100 text-emerald-800 px-2.5 py-1 rounded-full font-bold">Đã xếp lịch</span>
                                      <button 
                                        onClick={() => { 
                                          setSelectedCls({ name: item.course_name || 'Lớp học phần GA', code: item.course_code || 'GA', date: item.date || '03/09/2026', time: item.slot_code || 'Tiết 1-3', room: item.room_code || 'A303' }); 
                                          setIsReqModalOpen(true); 
                                        }} 
                                        className="text-[10px] bg-indigo-600 text-white font-bold px-3 py-1.5 rounded-lg hover:bg-indigo-700 transition"
                                      >
                                        Đổi lịch
                                      </button>
                                    </div>
                                  </div>
                                ))
                              ) : (
                                <div className="p-8 text-center text-xs text-slate-400 italic">
                                  Chưa có dữ liệu lịch. Vui lòng sang tài khoản Phòng Đào Tạo bấm chạy nút <strong>"Chạy thuật toán GA"</strong> trước!
                                </div>
                              )}
                            </div>
                          </div>
                        );
                      })()}

                  {/* 2. Weekly View Grid */}
                  {activeView === 'week' && (
                    <div className="space-y-4">
                      <div className="flex justify-between items-center bg-white p-4 rounded-2xl border shadow-xs">
                        <div>
                          <h3 className="text-base font-bold text-slate-800">Tuần 0{currentWeekOffset} (01/09/2026 - 07/09/2026)</h3>
                          <p className="text-xs text-slate-500">Học kỳ 1, Năm học 2026-2027</p>
                        </div>
                        <div className="flex items-center gap-2">
                          <button onClick={() => setCurrentWeekOffset(prev => Math.max(1, prev - 1))} className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-xs font-bold rounded-lg">&lt; Tuần trước</button>
                          <button onClick={() => setCurrentWeekOffset(4)} className="px-3 py-1.5 bg-indigo-50 text-indigo-700 text-xs font-bold rounded-lg">Tuần hiện tại</button>
                          <button onClick={() => setCurrentWeekOffset(prev => prev + 1)} className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-xs font-bold rounded-lg">Tuần sau &gt;</button>
                        </div>
                      </div>

                      <div className="grid grid-cols-7 gap-3">
                        {['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'Chủ Nhật'].map((day, idx) => (
                          <div key={idx} className="bg-white border rounded-xl p-2.5 min-h-[500px] flex flex-col justify-between shadow-xs">
                            <div className="text-center pb-2 border-b mb-2"><span className="text-[10px] font-bold text-slate-400 uppercase">{day}</span><p className="text-sm font-bold">0{idx + 3}/09</p></div>
                            <div className="flex-1 flex flex-col justify-center">
                              {idx === 0 && timetables.length > 0 ? (
                                <div onClick={() => openRequestModal('Lớp GA Tự động', 'GA_01', 'Thứ 2 (03/09)', 'Tiết 1-3', 'A303')} className="bg-indigo-50 border p-2 rounded-lg cursor-pointer hover:border-indigo-300">
                                  <span className="text-[9px] bg-indigo-600 text-white px-1 rounded font-bold">GA Lịch</span>
                                  <p className="font-bold text-[11px] text-indigo-900 mt-1">Xem chi tiết lịch GA</p>
                                </div>
                              ) : (
                                <div className="text-center py-4 text-slate-300 text-[10px] bg-slate-50/50 rounded-lg">Trống</div>
                              )}
                            </div>
                            <div className="flex-1 flex flex-col justify-center border-t pt-2"><div className="text-center py-4 text-slate-300 text-[10px] bg-slate-50/50 rounded-lg">Trống</div></div>
                            <div className="flex-1 flex flex-col justify-center border-t pt-2"><div className="text-center py-4 text-slate-300 text-[10px] bg-slate-50/50 rounded-lg">Trống</div></div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {activeView === 'day' && (
                    <div className="bg-white p-6 rounded-2xl border text-center text-xs text-slate-500">
                      Chế độ xem theo ngày đang đồng bộ với dữ liệu GA thực tế.
                    </div>
                  )}

                  {activeView === 'month' && (
                    <div className="bg-white p-8 rounded-2xl border shadow-xs text-center">
                      <h3 className="font-bold text-slate-800 text-lg mb-2">Lịch biểu Tháng 09/2026</h3>
                      <p className="text-xs text-slate-500">Hiển thị lịch tổng quan toàn bộ các lớp học trong tháng từ GA Engine.</p>
                    </div>
                  )}
                </>
              )}
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
        </main>
      </div>

      {/* Modal Tạo Request */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-slate-900/60 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-3xl max-w-md w-full p-6 space-y-4">
            <div className="flex justify-between items-center border-b pb-3">
              <h3 className="font-bold text-base">Tạo yêu cầu đổi lịch</h3>
              <button onClick={() => setIsModalOpen(false)}>✕</button>
            </div>
            <div className="bg-slate-50 p-3 rounded-xl text-xs space-y-1">
              <p><strong>Môn:</strong> {selectedClass.name} ({selectedClass.code})</p>
              <p><strong>Thời gian:</strong> {selectedClass.date} - {selectedClass.time} (Phòng {selectedClass.room})</p>
            </div>
            <input 
              type="text" 
              value={reasonText} 
              onChange={(e) => setReasonText(e.target.value)} 
              placeholder="Nhập lý do đổi lịch..." 
              className="w-full bg-slate-50 border rounded-xl px-3 py-2 text-xs outline-none focus:ring-2 focus:ring-indigo-600"
            />
            <button onClick={submitLecRequest} className="w-full bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold py-3 rounded-xl shadow">
              Gửi yêu cầu
            </button>
          </div>
        </div>
      )}
    </div>
  );
};