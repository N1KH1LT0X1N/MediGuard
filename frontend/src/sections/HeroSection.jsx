import { useGSAP } from "@gsap/react";
import gsap from "gsap";
import { SplitText } from "gsap/all";
import { useMediaQuery } from "react-responsive";

const HeroSection = () => {
  const isMobile = useMediaQuery({
    query: "(max-width: 768px)",
  });

  const isTablet = useMediaQuery({
    query: "(max-width: 1024px)",
  });

  useGSAP(() => {
    const titleSplit = SplitText.create(".hero-title", {
      type: "chars",
    });

    const tl = gsap.timeline({
      delay: 1,
    });

    tl.to(".hero-content", {
      opacity: 1,
      y: 0,
      ease: "power1.inOut",
    }).from(
      titleSplit.chars,
      {
        yPercent: 200,
        stagger: 0.02,
        ease: "power2.out",
      },
      "-=0.5"
    );

    const heroTl = gsap.timeline({
      scrollTrigger: {
        trigger: ".hero-container",
        start: "1% top",
        end: "bottom top",
        scrub: true,
      },
    });
    heroTl.to(".hero-container", {
      rotate: 7,
      scale: 0.9,
      yPercent: 30,
      ease: "power1.inOut",
    });

    // Background video removed per UI update — no play/pause animation required.
  });

  return (
    <section className="bg-main-bg">
      <div className="hero-container">
        <>
              {/* Background video removed; reserve the space so layout remains */}
              <div className="hero-bg-empty absolute inset-0 w-full h-full" aria-hidden="true" />
        </>
        <div className="hero-content opacity-0">
          <div className="overflow-hidden text-center px-4 md:px-0">
            <h1 className="hero-title">
              The Future of Cardiac Remote
              <br /> Monitoring: Empowered
              <br />
              <span className="by-line">
                <span className="by-text">by</span>
                <span className="brand-blue-big">MediGuard AI</span>
              </span>
            </h1>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
