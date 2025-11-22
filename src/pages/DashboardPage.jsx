import DashboardNavBar from '../components/DashboardNavBar';
import { Outlet } from 'react-router-dom';

const DashboardPage = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <DashboardNavBar />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>
    </div>
  );
};

export default DashboardPage;
