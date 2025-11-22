import { Link, useLocation } from 'react-router-dom';
import { useState } from 'react';

const DashboardNavBar = () => {
  const location = useLocation();
  const [activeRole, setActiveRole] = useState('doctor');
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="w-full bg-white shadow-md">
      {/* Single Navbar */}
      <div className="bg-[#7FFF00]">
        <div className="w-full px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-14">
            {/* Navigation Links - Evenly distributed */}
            <div className="flex items-center justify-evenly flex-1">
              <Link
                to="/dashboard/predict"
                className={`px-4 py-2 text-base font-bold whitespace-nowrap transition-colors duration-200 ${
                  isActive('/dashboard/predict')
                    ? 'text-black bg-[#6ee000] rounded'
                    : 'text-black hover:bg-[#6ee000] rounded'
                }`}
              >
                Predict Disease
              </Link>
              <Link
                to="/dashboard/overview"
                className={`px-4 py-2 text-base font-bold whitespace-nowrap transition-colors duration-200 ${
                  isActive('/dashboard/overview')
                    ? 'text-black bg-[#6ee000] rounded'
                    : 'text-black hover:bg-[#6ee000] rounded'
                }`}
              >
                Dashboard
              </Link>
              <Link
                to="/dashboard/reports"
                className={`px-4 py-2 text-base font-bold whitespace-nowrap transition-colors duration-200 ${
                  isActive('/dashboard/reports')
                    ? 'text-black bg-[#6ee000] rounded'
                    : 'text-black hover:bg-[#6ee000] rounded'
                }`}
              >
                Reports
              </Link>
              <Link
                to="/dashboard/appointments"
                className={`px-4 py-2 text-base font-bold whitespace-nowrap transition-colors duration-200 ${
                  isActive('/dashboard/appointments')
                    ? 'text-black bg-[#6ee000] rounded'
                    : 'text-black hover:bg-[#6ee000] rounded'
                }`}
              >
                Appointments
              </Link>
              <Link
                to="/dashboard/settings"
                className={`px-4 py-2 text-base font-bold whitespace-nowrap transition-colors duration-200 ${
                  isActive('/dashboard/settings')
                    ? 'text-black bg-[#6ee000] rounded'
                    : 'text-black hover:bg-[#6ee000] rounded'
                }`}
              >
                Settings
              </Link>
            </div>

            {/* Dropdown - Right Side */}
            <div className="relative ml-4">
              <button
                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                className="px-4 py-2 text-base font-bold text-black bg-[#7FFF00] rounded hover:bg-[#6ee000] transition-colors duration-200 flex items-center space-x-2"
              >
                <span>{activeRole === 'doctor' ? 'Doctor' : 'Patient'}</span>
                <svg
                  className={`w-4 h-4 transition-transform duration-200 ${isDropdownOpen ? 'rotate-180' : ''}`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {/* Dropdown Menu */}
              {isDropdownOpen && (
                <div className="absolute right-0 mt-2 w-40 bg-black rounded-md shadow-lg z-10">
                  <button
                    onClick={() => {
                      setActiveRole('doctor');
                      setIsDropdownOpen(false);
                    }}
                    className={`block w-full text-left px-4 py-2 text-sm font-medium hover:bg-gray-800 rounded-t-md ${
                      activeRole === 'doctor' ? 'bg-gray-800 text-[#7FFF00]' : 'text-white'
                    }`}
                  >
                    Doctor
                  </button>
                  <button
                    onClick={() => {
                      setActiveRole('patient');
                      setIsDropdownOpen(false);
                    }}
                    className={`block w-full text-left px-4 py-2 text-sm font-medium hover:bg-gray-800 rounded-b-md ${
                      activeRole === 'patient' ? 'bg-gray-800 text-[#7FFF00]' : 'text-white'
                    }`}
                  >
                    Patient
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default DashboardNavBar;
