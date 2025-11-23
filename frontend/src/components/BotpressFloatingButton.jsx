import { useState, useEffect } from 'react';
import { Bot } from 'lucide-react';

const BotpressFloatingButton = () => {
  const [showTooltip, setShowTooltip] = useState(false);

  useEffect(() => {
    // Hide the default Botpress button if it exists
    const hideDefaultButton = () => {
      // Try multiple selectors to find Botpress widget
      const selectors = [
        '[data-bp-widget]',
        '.bp-widget-container',
        '[id*="botpress"]',
        '[id*="bp-"]',
        'iframe[src*="botpress"]',
        '[class*="bp-"]',
        '[class*="botpress"]',
      ];

      selectors.forEach(selector => {
        const elements = document.querySelectorAll(selector);
        elements.forEach(element => {
          // Hide the entire widget container
          if (element) {
            element.style.display = 'none';
            element.style.visibility = 'hidden';
            element.style.opacity = '0';
            element.style.pointerEvents = 'none';
            
            // Also hide any buttons inside
            const buttons = element.querySelectorAll('button');
            buttons.forEach(btn => {
              btn.style.display = 'none';
              btn.style.visibility = 'hidden';
            });
          }
        });
      });

      // Also check for iframes that might contain the widget
      const iframes = document.querySelectorAll('iframe');
      iframes.forEach(iframe => {
        if (iframe.src && iframe.src.includes('botpress')) {
          iframe.style.display = 'none';
        }
      });
    };

    // Try to hide default button immediately and continuously
    hideDefaultButton();
    const interval = setInterval(() => {
      hideDefaultButton();
    }, 200);

    // Also use MutationObserver to catch dynamically added elements
    const observer = new MutationObserver(() => {
      hideDefaultButton();
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
    });

    // Cleanup
    return () => {
      clearInterval(interval);
      observer.disconnect();
    };
  }, []);

  const handleClick = () => {
    // Try multiple methods to open Botpress chat
    if (window.botpress?.webchat?.open) {
      window.botpress.webchat.open();
    } else if (window.botpress?.webchat) {
      // Alternative method
      const event = new Event('click', { bubbles: true });
      const widget = window.botpress.webchat;
      if (widget) widget.open();
    } else {
      // Fallback: find and click the Botpress button
      const chatButton = document.querySelector('[data-bp-widget] button') || 
                        document.querySelector('.bp-widget-container button') ||
                        document.querySelector('[id*="botpress"] button') ||
                        document.querySelector('button[aria-label*="chat"]');
      if (chatButton) {
        chatButton.click();
      } else {
        // Last resort: dispatch a custom event
        window.dispatchEvent(new CustomEvent('botpress:open'));
      }
    }
  };

  return (
    <div className="fixed bottom-28 right-6 z-50 md:right-6 sm:right-4">
      {/* Tooltip */}
      {showTooltip && (
        <div
          className="absolute bottom-full right-0 mb-3 px-4 py-2 bg-gray-900 text-white text-sm font-medium rounded-lg whitespace-nowrap shadow-xl"
          style={{
            animation: 'fadeIn 0.2s ease-out',
          }}
        >
          Chat with Bot
          {/* Arrow */}
          <div className="absolute top-full right-5 w-0 h-0 border-l-[6px] border-r-[6px] border-t-[6px] border-transparent border-t-gray-900"></div>
        </div>
      )}
      
      <button
        onClick={handleClick}
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        className="bg-[#6366F1] hover:bg-[#4F46E5] text-white rounded-full p-4 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-110 flex items-center justify-center"
        style={{
          width: '64px',
          height: '64px',
          boxShadow: '0 4px 12px rgba(99, 102, 241, 0.4)',
        }}
        aria-label="Open chatbot"
      >
        <Bot className="w-8 h-8" />
      </button>
    </div>
  );
};

export default BotpressFloatingButton;

