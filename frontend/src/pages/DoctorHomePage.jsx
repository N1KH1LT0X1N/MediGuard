import DoctorNavBar from '../components/DoctorNavBar';
import { Outlet } from 'react-router-dom';

const DoctorHomePage = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <DoctorNavBar />
      <main className="w-full px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>
    </div>
  );
};

export default DoctorHomePage;
