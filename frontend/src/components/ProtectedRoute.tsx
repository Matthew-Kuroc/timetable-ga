import { Navigate, Outlet } from 'react-router-dom';

interface Props {
  allowedRoles: string[];
}

export const ProtectedRoute = ({ allowedRoles }: Props) => {
  const token = localStorage.getItem('access_token');
  const role = localStorage.getItem('user_role'); // Nhận từ FastAPI trả về

  if (!token) return <Navigate to="/login" replace />;
  if (!role || !allowedRoles.includes(role)) return <Navigate to="/login" replace />;

  return <Outlet />;
};