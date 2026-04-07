"use client";
import {useRef} from "react";

export default function Likes() {
    const likesRef = useRef<HTMLDivElement | null>(null);

      const scroll = (
        ref: React.RefObject<HTMLDivElement | null>,
        dir: "left" | "right") => {
            if (ref.current) {
                ref.current.scrollBy({
                    left: dir === "left" ? -700 : 700,
                    behavior: "smooth",
        });
      }
    };

    return (
    <div className="flex flex-col gap-1 w-full rounded-lg px-2 py-1 relative"> 
          <h2 className="text-2xl font-bold text-text-light mb-1">Your Likes</h2>
          <button onClick={() => scroll(likesRef, "left")}
            className="absolute -left-10 top-[60%] -translate-y-1/2 z-10 bg-black/50 text-white px-2 py-1 rounded hover:cursor-pointer">
              ←
          </button> 
          <div ref={likesRef} className="flex flex-row gap-5 overflow-x-auto scroll-smooth snap-x snap-mandatory no-scrollbar py-2">
            <div className="bg-box border rounded-lg p-4 w-45 h-65 flex-shrink-0 snap-start hover:cursor-pointer hover:scale-[1.02] transition-transform duration-200">
              Movie 1
            </div>
            <div className="bg-box border rounded-lg p-4 w-45 h-65 flex-shrink-0 snap-start hover:cursor-pointer hover:scale-[1.02] transition-transform duration-200">
              Movie 2
            </div>
            <div className="bg-box border rounded-lg p-4 w-45 h-65 flex-shrink-0 snap-start hover:cursor-pointer hover:scale-[1.02] transition-transform duration-200">
              Movie 3
            </div>
            <div className="bg-box border rounded-lg p-4 w-45 h-65 flex-shrink-0 snap-start hover:cursor-pointer hover:scale-[1.02] transition-transform duration-200">
              Movie 4
            </div>
            <div className="bg-box border rounded-lg p-4 w-45 h-65 flex-shrink-0 snap-start hover:cursor-pointer hover:scale-[1.02] transition-transform duration-200">
              Movie 5
            </div>
            <div className="bg-box border rounded-lg p-4 w-45 h-65 flex-shrink-0 snap-start hover:cursor-pointer hover:scale-[1.02] transition-transform duration-200">
              Movie 6
            </div>
          </div>
          <button onClick={() => scroll(likesRef, "right")}
            className="absolute -right-10 top-[60%] -translate-y-1/2 z-10 bg-black/50 text-white px-2 py-1 rounded hover:cursor-pointer">
              →
          </button>
    </div>
  );
}