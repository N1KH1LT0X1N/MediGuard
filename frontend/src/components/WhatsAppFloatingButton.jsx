import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { MessageCircle } from 'lucide-react';

const WhatsAppFloatingButton = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [showTooltip, setShowTooltip] = useState(false);

  // Hide button on WhatsApp page itself
  if (location.pathname === '/whatsapp') {
    return null;
  }

  const handleClick = () => {
    navigate('/whatsapp');
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 md:right-6 sm:right-4">
      {/* Tooltip */}
      {showTooltip && (
        <div
          className="absolute bottom-full right-0 mb-3 px-4 py-2 bg-gray-900 text-white text-sm font-medium rounded-lg whitespace-nowrap shadow-xl"
          style={{
            animation: 'fadeIn 0.2s ease-out',
          }}
        >
          WhatsApp Chatbot
          {/* Arrow */}
          <div className="absolute top-full right-5 w-0 h-0 border-l-[6px] border-r-[6px] border-t-[6px] border-transparent border-t-gray-900"></div>
        </div>
      )}
      
      <button
        onClick={handleClick}
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        className="bg-[#25D366] hover:bg-[#20BA5A] text-white rounded-full p-4 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-110 flex items-center justify-center"
        style={{
          width: '64px',
          height: '64px',
          boxShadow: '0 4px 12px rgba(37, 211, 102, 0.4)',
        }}
        aria-label="Open WhatsApp support"
      >
        <MessageCircle className="w-8 h-8" />
      </button>
    </div>
  );
};

export default WhatsAppFloatingButton;

