import { useNavigate } from 'react-router-dom';

const NavBar = () => {
  const navigate = useNavigate();

  const handleGetStarted = () => {
    navigate('/home');
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 md:p-6 p-3">
      <div className="flex justify-end items-center">
        <button className="nav-cta" onClick={handleGetStarted}>
          Get Started
        </button>
      </div>
    </nav>
  );
};

export default NavBar;
