import { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, MessageCircle, Smartphone, ScanLine, CheckCircle2 } from 'lucide-react';
import { useGSAP } from '@gsap/react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/all';

gsap.registerPlugin(ScrollTrigger);

const WhatsAppPage = () => {
  const navigate = useNavigate();
  const containerRef = useRef(null);
  const qrSectionRef = useRef(null);
  const stepsRef = useRef([]);

  const steps = [
    {
      number: 1,
      title: 'Open WhatsApp',
      description: 'Open the WhatsApp application on your smartphone',
      icon: <Smartphone className="w-6 h-6" />,
    },
    {
      number: 2,
      title: 'Scan QR Code',
      description: 'Tap on the three dots menu and select "Linked Devices" or "WhatsApp Web"',
      icon: <ScanLine className="w-6 h-6" />,
    },
    {
      number: 3,
      title: 'Point Camera',
      description: 'Point your camera at the QR code displayed on this page',
      icon: <MessageCircle className="w-6 h-6" />,
    },
    {
      number: 4,
      title: 'Start Chatting',
      description: 'Once connected, you can start chatting with our support team',
      icon: <CheckCircle2 className="w-6 h-6" />,
    },
  ];

  useGSAP(() => {
    if (!containerRef.current) return;

    const ctx = gsap.context(() => {
      // Animate title section
      gsap.from('.whatsapp-title-section', {
        y: -40,
        opacity: 0,
        duration: 0.8,
        ease: 'power2.out',
      });

      // Animate QR code section
      gsap.from('.whatsapp-qr-section', {
        scale: 0.9,
        opacity: 0,
        duration: 0.8,
        ease: 'power2.out',
        scrollTrigger: {
          trigger: '.whatsapp-qr-section',
          start: 'top 85%',
          toggleActions: 'play none none none',
        },
      });

      // Animate steps with stagger - using opacity and y instead of x to avoid blur
      gsap.from('.whatsapp-step', {
        y: 30,
        opacity: 0,
        duration: 0.8,
        stagger: 0.15,
        ease: 'power2.out',
        scrollTrigger: {
          trigger: '.whatsapp-steps-container',
          start: 'top 85%',
          toggleActions: 'play none none none',
        },
      });

      // Animate help section
      gsap.from('.whatsapp-help-section', {
        y: 40,
        opacity: 0,
        duration: 0.8,
        ease: 'power2.out',
        scrollTrigger: {
          trigger: '.whatsapp-help-section',
          start: 'top 90%',
          toggleActions: 'play none none none',
        },
      });
    }, containerRef);

    return () => ctx.revert();
  }, []);

  return (
    <div ref={containerRef} className="min-h-screen bg-white">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center text-gray-600 hover:text-gray-900 transition-colors group"
          >
            <ArrowLeft className="w-5 h-5 mr-2 group-hover:-translate-x-1 transition-transform" />
            <span>Back</span>
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        {/* Title Section */}
        <div className="whatsapp-title-section text-center mb-16">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-[#9CFB4B] rounded-full mb-6">
            <MessageCircle className="w-10 h-10 text-black" />
          </div>
          <h1 
            className="text-gray-900 mb-4"
            style={{ 
              fontWeight: 300, 
              fontSize: 'clamp(2.6rem, 6.5vw, 6.8rem)', 
              lineHeight: 1.05, 
              letterSpacing: '-0.005em' 
            }}
          >
            Connect with Us on
            <br />
            <span style={{ fontWeight: 600, color: '#9CFB4B' }}>WhatsApp</span>
          </h1>
          <p 
            className="text-gray-600 max-w-2xl mx-auto"
            style={{ fontSize: 'clamp(1rem, 2vw, 1.25rem)', lineHeight: 1.6 }}
          >
            Scan the QR code below to start a conversation with our support team. 
            We're here to help you with any questions or concerns.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-12 items-start mb-16">
          {/* QR Code Section */}
          <div 
            ref={qrSectionRef}
            className="whatsapp-qr-section bg-white rounded-2xl shadow-lg p-8 border-2 border-gray-200 hover:border-[#9CFB4B] transition-all duration-300"
            style={{
              boxShadow: '0 10px 25px rgba(0, 0, 0, 0.1)',
            }}
          >
            <h2 
              className="text-gray-900 mb-6 text-center font-semibold"
              style={{ 
                fontSize: 'clamp(1.5rem, 3vw, 2rem)',
                WebkitFontSmoothing: 'antialiased',
                MozOsxFontSmoothing: 'grayscale',
                textRendering: 'optimizeLegibility',
                backfaceVisibility: 'hidden',
                transform: 'translateZ(0)',
              }}
            >
              Scan QR Code
            </h2>
            <div className="flex justify-center items-center bg-white p-6 md:p-8 rounded-lg border-2 border-gray-200">
              <img 
                src="/images/whatsapp-qr.png" 
                alt="WhatsApp QR Code - Scan to connect"
                className="w-full max-w-md"
                style={{ 
                  display: 'block',
                  width: '100%',
                  maxWidth: '500px',
                  height: 'auto',
                  aspectRatio: '1 / 1',
                  objectFit: 'contain',
                  imageRendering: '-webkit-optimize-contrast',
                  imageRendering: 'crisp-edges',
                }}
              />
            </div>
            <p className="text-sm text-gray-500 text-center mt-4">
              Use WhatsApp to scan this code
            </p>
          </div>

          {/* Steps Section */}
          <div className="whatsapp-steps-container space-y-6">
            <h2 
              className="text-gray-900 mb-8 font-semibold"
              style={{ fontSize: 'clamp(1.5rem, 3vw, 2rem)' }}
            >
              How to Connect
            </h2>
            {steps.map((step, index) => (
              <div
                key={step.number}
                ref={(el) => (stepsRef.current[index] = el)}
                className="whatsapp-step flex gap-4 p-6 bg-white rounded-xl border-2 border-gray-200 hover:border-[#9CFB4B] transition-colors duration-300 group cursor-pointer"
                style={{
                  boxShadow: '0 2px 8px rgba(0, 0, 0, 0.05)',
                  WebkitFontSmoothing: 'antialiased',
                  MozOsxFontSmoothing: 'grayscale',
                  textRendering: 'optimizeLegibility',
                }}
                onMouseEnter={(e) => {
                  // Use translateY instead of scale to avoid blur
                  gsap.to(e.currentTarget, {
                    y: -4,
                    boxShadow: '0 10px 25px rgba(156, 251, 75, 0.2)',
                    duration: 0.3,
                    force3D: true,
                    autoRound: false,
                  });
                }}
                onMouseLeave={(e) => {
                  gsap.to(e.currentTarget, {
                    y: 0,
                    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.05)',
                    duration: 0.3,
                    force3D: true,
                    autoRound: false,
                  });
                }}
              >
                <div className="flex-shrink-0">
                  <div 
                    className="w-12 h-12 rounded-full flex items-center justify-center text-black font-bold text-lg transition-colors"
                    style={{ backgroundColor: '#9CFB4B' }}
                  >
                    {step.number}
                  </div>
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <div style={{ color: '#9CFB4B' }}>
                      {step.icon}
                    </div>
                    <h3 
                      className="text-lg font-semibold text-gray-900"
                      style={{
                        WebkitFontSmoothing: 'antialiased',
                        MozOsxFontSmoothing: 'grayscale',
                        textRendering: 'optimizeLegibility',
                        backfaceVisibility: 'hidden',
                        transform: 'translateZ(0)',
                      }}
                    >
                      {step.title}
                    </h3>
                  </div>
                  <p 
                    className="text-gray-600"
                    style={{
                      WebkitFontSmoothing: 'antialiased',
                      MozOsxFontSmoothing: 'grayscale',
                      textRendering: 'optimizeLegibility',
                      backfaceVisibility: 'hidden',
                      transform: 'translateZ(0)',
                    }}
                  >
                    {step.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Additional Info */}
        <div 
          className="whatsapp-help-section bg-white rounded-xl p-8 border-2 border-gray-200"
          style={{
            backgroundColor: 'rgba(156, 251, 75, 0.1)',
            borderColor: 'rgba(156, 251, 75, 0.3)',
          }}
        >
          <div className="flex items-start gap-4">
            <MessageCircle 
              className="w-6 h-6 flex-shrink-0 mt-1" 
              style={{ color: '#9CFB4B' }}
            />
            <div>
              <h3 className="font-semibold text-gray-900 mb-2 text-lg">
                Need Help?
              </h3>
              <p className="text-gray-600">
                If you're having trouble scanning the QR code, make sure your phone's camera 
                has permission to access WhatsApp, and that you're using the latest version 
                of the WhatsApp app.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WhatsAppPage;
