"use client";

import {useRef, useEffect, useState} from "react";
import {useRouter} from "next/navigation";
import {FaArrowLeftLong, FaArrowRightLong} from "react-icons/fa6";
import {supabase} from "../lib/supabase";
import {useLikes} from "../lib/useLikes";
import LikeButton from "./LikeButton";

type Movie = {
  slug: string;
  title: string;
  poster_filename?: string;
};

export default function Likes() {
  const likesRef = useRef<HTMLDivElement | null>(null);
  const {likedSlugs} = useLikes();
  const [movies, setMovies] = useState<Movie[]>([]);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  useEffect(() => {
    if (!likedSlugs.length) {
      setMovies([]);
      return;
    }

    const fetchMovies = async () => {
      setLoading(true);
      const {data, error} = await supabase
        .from("movies")
        .select("slug, title, poster_filename")
        .in("slug", likedSlugs);

      if (!error && data) {
        setMovies(data);
      }
      setLoading(false);
    };

    fetchMovies();
  }, [likedSlugs]);

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
      {likedSlugs.length === 0 ? (
        <div className="h-65 flex items-center justify-center text-sm text-gray-400">
          Like some movies to see them here
        </div>
      ) : (
        <>
          <button onClick={() => scroll(likesRef, "left")}
            className="absolute -left-10 top-[60%] -translate-y-1/2 z-10 bg-black/50 text-white px-2 py-1 rounded hover:cursor-pointer">
            <FaArrowLeftLong/>
          </button>
          <div ref={likesRef} className="flex flex-row gap-5 overflow-x-auto scroll-smooth snap-x snap-mandatory no-scrollbar py-2">
            {movies.map((movie) => (
          <div
            key={movie.slug}
            onClick={() => router.push(`/movie/${movie.slug}`)}
            className="relative group w-45 h-65 flex-shrink-0 snap-start hover:cursor-pointer hover:scale-[1.02] transition-transform duration-200 flex flex-col"
          >
            <div className="absolute top-0 w-full bg-black/60 text-white text-xs p-1 text-center line-clamp-2 z-20">
              {movie.title}
            </div>
            {movie.poster_filename && (
              <>
                <img
                  src={`https://qivcmhdrljwmpwujkwqd.supabase.co/storage/v1/object/public/Wiki_Images/wikipedia_images/${movie.poster_filename}`}
                  alt={movie.title}
                  className="w-full h-full object-cover rounded-md bg-box/95"
                />
                <div className="absolute inset-0 bg-gray-900/50 opacity-0 group-hover:opacity-100 transition rounded-md" />
                <div className="absolute bottom-2 right-2 z-10">
                  <LikeButton slug={movie.slug}/>
                </div>
              </>
            )}
            {!movie.poster_filename && (
              <div className="w-full h-full bg-box/95 border rounded-md flex items-center justify-center">
                <span className="text-sm text-gray-400">{movie.title}</span>
              </div>
            )}
          </div>
        ))}
      </div>
          <button onClick={() => scroll(likesRef, "right")}
            className="absolute -right-10 top-[60%] -translate-y-1/2 z-10 bg-black/50 text-white px-2 py-1 rounded hover:cursor-pointer">
            <FaArrowRightLong/>
          </button>
        </>
      )}
    </div>
  );
}