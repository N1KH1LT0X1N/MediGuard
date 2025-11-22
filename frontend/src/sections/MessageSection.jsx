import { useGSAP } from "@gsap/react";
import gsap from "gsap";
import { SplitText } from "gsap/all";

const MessageSection = () => {
  useGSAP(() => {
    // Use SplitText to reveal headings line-by-line on scroll
    const firstLineSplit = SplitText.create(".first-message", {
      type: "lines",
      linesClass: "line-line",
    });
    const secondLineSplit = SplitText.create(".second-message", {
      type: "lines",
      linesClass: "line-line",
    });

    // ensure lines are hidden initially (we'll animate them in)
    gsap.set([...firstLineSplit.lines, ...secondLineSplit.lines], {
      autoAlpha: 0,
      y: 40,
    });

    // timeline: first heading lines -> tape reveal -> second heading lines
    const seq = gsap.timeline({
      scrollTrigger: {
        trigger: ".message-content",
        start: "top 80%",
        toggleActions: "play none none reverse",
      },
    });

    seq.to(firstLineSplit.lines, {
      autoAlpha: 1,
      y: 0,
      stagger: 0.06,
      duration: 0.55,
      ease: "power2.out",
    })
      .to(
        ".msg-text-scroll",
        {
          duration: 0.6,
          clipPath: "polygon(0% 0%, 100% 0%, 100% 100%, 0% 100%)",
          ease: "circ.inOut",
        },
        "-=" + 0.15
      )
      .to(secondLineSplit.lines, {
        autoAlpha: 1,
        y: 0,
        stagger: 0.06,
        duration: 0.55,
        ease: "power2.out",
      },
      "-=" + 0.15);
  });

  return (
    <section className="message-content">
      <div className="container mx-auto flex-center py-28 relative">
        <div className="w-full h-full">
          <div className="msg-wrapper">
            <h1 className="first-message">INSTANT, EXPLAINABLE TRIAGE</h1>

            <div
              style={{
                clipPath: "polygon(0 0, 0 0, 0 100%, 0% 100%)",
              }}
              className="msg-text-scroll"
            >
              <div className="bg-light-brown md:pb-5 pb-3 px-5">
                <h2 className="text-red-brown">MEDIGUARD AI</h2>
              </div>
            </div>

            <h1 className="second-message">
              SMART RISK SCORES FOR FASTER CLINICAL DECISIONS
            </h1>
          </div>

          {/* paragraph removed per request */}
        </div>
      </div>
    </section>
  );
};

export default MessageSection;
