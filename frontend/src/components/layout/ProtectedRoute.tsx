import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import BottomNav from "./BottomNav";

export default function ProtectedRoute() {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) return <div className="loading-screen">Loading...</div>;
  if (!isAuthenticated)
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;

  return (
    <div className="app-layout">
      <main className="app-content">
        <Outlet />
      </main>
      <BottomNav />
    </div>
  );
}
