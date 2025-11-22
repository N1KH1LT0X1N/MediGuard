import NavBar from '../components/NavBar';
import HeroSection from '../sections/HeroSection';
import MessageSection from '../sections/MessageSection';
import FooterSection from '../sections/FooterSection';
import { ScrollSmoother, ScrollTrigger } from "gsap/all";
import gsap from "gsap";
import { useGSAP } from "@gsap/react";

gsap.registerPlugin(ScrollTrigger, ScrollSmoother);

const HomePage = () => {
  useGSAP(() => {
    ScrollSmoother.create({
      smooth: 3,
      effects: true,
    });
  });

  return (
    <>
      <NavBar />
      <div id="smooth-wrapper">
        <div id="smooth-content">
          <HeroSection />
          <MessageSection />
          <FooterSection />
        </div>
      </div>
    </>
  );
};

export default HomePage;
