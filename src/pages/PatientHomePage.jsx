import PatientNavBar from '../components/PatientNavBar';
import { Outlet } from 'react-router-dom';

const PatientHomePage = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <PatientNavBar />
      <main className="w-full px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>
    </div>
  );
};

export default PatientHomePage;
