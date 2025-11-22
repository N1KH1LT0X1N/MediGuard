import { useState, useEffect, useRef } from 'react';
import { cn } from '../../lib/utils';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/all';

gsap.registerPlugin(ScrollTrigger);

export const CategoryList = ({
  title,
  subtitle,
  categories,
  headerIcon,
  className,
}) => {
  const [hoveredItem, setHoveredItem] = useState(null);
  const containerRef = useRef(null);
  const cardsRef = useRef([]);

  useEffect(() => {
    if (!containerRef.current) return;

    const ctx = gsap.context(() => {
      // Animate header
      gsap.from('.category-header', {
        y: -40,
        opacity: 0,
        duration: 0.8,
        ease: 'power2.out',
        scrollTrigger: {
          trigger: containerRef.current,
          start: 'top 90%',
          toggleActions: 'play none none none',
        },
      });

      // Animate cards with stagger
      gsap.from('.category-card', {
        y: 60,
        opacity: 0,
        duration: 0.8,
        stagger: 0.15,
        ease: 'power2.out',
        scrollTrigger: {
          trigger: '.category-cards-container',
          start: 'top 85%',
          toggleActions: 'play none none none',
        },
      });
    }, containerRef);

    return () => ctx.revert();
  }, []);

  return (
    <div ref={containerRef} className={cn("w-full bg-white text-black p-8", className)}>
      <div className="w-full px-4 md:px-8 lg:px-16">
        {/* Header Section */}
        <div className="category-header text-center mb-12 md:mb-16">
          {headerIcon && (
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-gray-800 to-gray-900 mb-6 text-white">
              {headerIcon}
            </div>
          )}
          <h1 className="text-black" style={{ fontWeight: 300, fontSize: 'clamp(2.6rem, 6.5vw, 6.8rem)', lineHeight: 1.05, letterSpacing: '-0.005em' }}>{title}</h1>
          {subtitle && (
            <h2 style={{ fontWeight: 600, fontSize: 'clamp(3rem, 8vw, 7rem)', lineHeight: 0.9, color: '#7FFF00' }}>{subtitle}</h2>
          )}
        </div>

        {/* Categories List */}
        <div className="category-cards-container space-y-6">
          {categories.map((category) => (
            <div
              key={category.id}
              className="category-card relative group"
              onMouseEnter={() => setHoveredItem(category.id)}
              onMouseLeave={() => setHoveredItem(null)}
              onClick={category.onClick}
            >
              <div
                className={cn(
                  "relative overflow-hidden border bg-white transition-all duration-300 ease-in-out cursor-pointer",
                  hoveredItem === category.id
                    ? 'h-40 shadow-lg bg-gray-50'
                    : 'h-32 border-gray-300'
                )}
                style={hoveredItem === category.id ? { borderColor: '#7FFF00', boxShadow: '0 10px 15px -3px rgba(127, 255, 0, 0.2)' } : {}}
              >
                {/* Corner brackets that appear on hover */}
                {hoveredItem === category.id && (
                  <>
                    <div className="absolute top-3 left-3 w-6 h-6">
                      <div className="absolute top-0 left-0 w-4 h-0.5" style={{ backgroundColor: '#7FFF00' }} />
                      <div className="absolute top-0 left-0 w-0.5 h-4" style={{ backgroundColor: '#7FFF00' }} />
                    </div>
                    <div className="absolute bottom-3 right-3 w-6 h-6">
                      <div className="absolute bottom-0 right-0 w-4 h-0.5" style={{ backgroundColor: '#7FFF00' }} />
                      <div className="absolute bottom-0 right-0 w-0.5 h-4" style={{ backgroundColor: '#7FFF00' }} />
                    </div>
                  </>
                )}

                {/* Content */}
                <div className="flex items-center justify-between h-full px-6 md:px-8">
                  <div className="flex-1">
                    <h3
                      className={cn(
                        "font-bold transition-colors duration-300",
                        category.featured ? 'text-2xl md:text-3xl' : 'text-xl md:text-2xl',
                        hoveredItem === category.id ? 'text-black' : 'text-black'
                      )}
                    >
                      {category.title}
                    </h3>
                    {category.subtitle && (
                      <p
                        className={cn(
                          "mt-1 transition-colors duration-300 text-sm md:text-base",
                           hoveredItem === category.id ? 'text-black' : 'text-black'
                        )}
                      >
                        {category.subtitle}
                      </p>
                    )}
                  </div>

                  {/* Icon appears on the right on hover */}
                  {category.icon && hoveredItem === category.id && (
                    <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-300" style={{ color: '#7FFF00' }}>
                      {category.icon}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
