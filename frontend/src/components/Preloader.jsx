import { useState, useEffect, useRef } from 'react';

const Preloader = ({ onComplete }) => {
  const [isVisible, setIsVisible] = useState(true);
  const videoRef = useRef(null);

  useEffect(() => {
    const video = videoRef.current;
    
    if (video) {
      // Play the video
      video.play().catch(err => {
        console.error('Error playing preloader video:', err);
        // If video fails to play, hide preloader after a short delay
        setTimeout(() => {
          setIsVisible(false);
          onComplete();
        }, 2000);
      });

      // Hide preloader when video ends
      const handleVideoEnd = () => {
        setIsVisible(false);
        onComplete();
      };

      video.addEventListener('ended', handleVideoEnd);

      // Fallback: hide preloader after 5 seconds max
      const timeout = setTimeout(() => {
        setIsVisible(false);
        onComplete();
      }, 5000);

      return () => {
        video.removeEventListener('ended', handleVideoEnd);
        clearTimeout(timeout);
      };
    }
  }, [onComplete]);

  if (!isVisible) {
    return null;
  }

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        backgroundColor: '#ffffff',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        zIndex: 9999,
      }}
    >
      <video
        id="preloader-video"
        ref={videoRef}
        width="600"
        height="600"
        autoPlay
        muted
        playsInline
        style={{
          maxWidth: '600px',
          maxHeight: '600px',
          width: '600px',
          height: '600px',
          objectFit: 'contain',
        }}
      >
        <source src="/videos/preloader.mp4" type="video/mp4" />
        Your browser does not support the video tag.
      </video>
    </div>
  );
};

export default Preloader;

