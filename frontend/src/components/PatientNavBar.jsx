import { Link, useLocation } from 'react-router-dom';

const PatientNavBar = () => {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="w-full bg-white shadow-md">
      <div className="bg-[#7FFF00]">
        <div className="w-full px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-14">
            {/* Navigation Links - Evenly distributed */}
            <div className="flex items-center justify-evenly flex-1">
              <Link
                to="/home/patient/dashboard"
                className={`px-4 py-2 text-base font-bold whitespace-nowrap transition-colors duration-200 ${
                  isActive('/home/patient/dashboard')
                    ? 'text-black bg-[#6ee000] rounded'
                    : 'text-black hover:bg-[#6ee000] rounded'
                }`}
              >
                Dashboard
              </Link>
              <Link
                to="/home/patient/predict"
                className={`px-4 py-2 text-base font-bold whitespace-nowrap transition-colors duration-200 ${
                  isActive('/home/patient/predict')
                    ? 'text-black bg-[#6ee000] rounded'
                    : 'text-black hover:bg-[#6ee000] rounded'
                }`}
              >
                Predict Disease
              </Link>
              <Link
                to="/home/patient/appointments"
                className={`px-4 py-2 text-base font-bold whitespace-nowrap transition-colors duration-200 ${
                  isActive('/home/patient/appointments')
                    ? 'text-black bg-[#6ee000] rounded'
                    : 'text-black hover:bg-[#6ee000] rounded'
                }`}
              >
                Appointments
              </Link>
              <Link
                to="/home/patient/reports"
                className={`px-4 py-2 text-base font-bold whitespace-nowrap transition-colors duration-200 ${
                  isActive('/home/patient/reports')
                    ? 'text-black bg-[#6ee000] rounded'
                    : 'text-black hover:bg-[#6ee000] rounded'
                }`}
              >
                Reports
              </Link>
              <Link
                to="/home/patient/doctors"
                className={`px-4 py-2 text-base font-bold whitespace-nowrap transition-colors duration-200 ${
                  isActive('/home/patient/doctors')
                    ? 'text-black bg-[#6ee000] rounded'
                    : 'text-black hover:bg-[#6ee000] rounded'
                }`}
              >
                Find Doctors
              </Link>
              <Link
                to="/home/patient/settings"
                className={`px-4 py-2 text-base font-bold whitespace-nowrap transition-colors duration-200 ${
                  isActive('/home/patient/settings')
                    ? 'text-black bg-[#6ee000] rounded'
                    : 'text-black hover:bg-[#6ee000] rounded'
                }`}
              >
                Settings
              </Link>
            </div>

            {/* Role Badge - Right Side */}
            <div className="ml-4">
              <Link
                to="/home/doctor"
                className="px-4 py-2 text-base font-bold text-black bg-[#7FFF00] rounded hover:bg-[#6ee000] transition-colors duration-200"
              >
                Switch to Doctor
              </Link>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default PatientNavBar;
