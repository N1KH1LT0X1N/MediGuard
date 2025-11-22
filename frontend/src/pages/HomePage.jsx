import NavBar from '../components/NavBar';
import HeroSection from '../sections/HeroSection';
import MessageSection from '../sections/MessageSection';
import FooterSection from '../sections/FooterSection';
import { CategoryList } from '../components/ui/CategoryList';
import { LayoutGrid, Bot, Code, Palette, ArrowRight } from 'lucide-react';
import { ScrollSmoother, ScrollTrigger } from "gsap/all";
import gsap from "gsap";
import { useGSAP } from "@gsap/react";

gsap.registerPlugin(ScrollTrigger, ScrollSmoother);

const HomePage = () => {
  const categories = [
    {
      id: 1,
      title: 'OCR Document Analysis',
      subtitle: 'Upload reports to automatically extract values and predict diseases. Supports images and CSV files.',
      onClick: () => alert('Navigating to OCR Analysis...'),
      icon: <ArrowRight className="w-8 h-8" />,
      featured: true,
    },
    {
      id: 2,
      title: 'AI Health Assistant',
      subtitle: 'RAG-powered chatbot that retrieves information from your reports and answers disease-related queries.',
      onClick: () => alert('Navigating to AI Assistant...'),
      icon: <Bot className="w-8 h-8" />,
    },
    {
      id: 3,
      title: 'Blockchain Medical Records',
      subtitle: 'Immutable logging of AI predictions with timestamped hashes for auditable, non-repudiable records.',
      onClick: () => alert('Navigating to Blockchain Records...'),
      icon: <Palette className="w-8 h-8" />,
    },
  ];

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
          <CategoryList
            title="Explore Our"
            subtitle="Core Features"
            categories={categories}
            headerIcon={<LayoutGrid className="w-8 h-8" />}
            className="py-16"
          />
          <FooterSection />
        </div>
      </div>
    </>
  );
};

export default HomePage;
