// import movies from "../../../../movies.json";                            // import JSON dataset containing all movies 

"use client";                                                               // needed for client-specific features like interactivity, state, event handlers 

import {supabase} from '../../../lib/supabase';                             // import Supabase client
import {use, useEffect, useState} from 'react';
import {useRouter} from "next/navigation";                                  // import this for back button
import MovieRec from "../../../components/MovieRec";
import LikeButton from "../../../components/LikeButton";

import {FaArrowLeftLong} from "react-icons/fa6";

export const dynamicParams = true;                                          // allow dynamic parameters, allows pages to be generated for any slug

// export default async function page({params}: {params: any}) {
//   const { slug } = await params;                                          // extract movie slug from URL
//   const movie = movies.find((m) => m.slug?.trim() === slug?.trim());      // search movies array for movie whose slug matches 

type SlugParams = {slug: string};

export default function Page({params}: {params: any}) {
  const {slug} = use(params) as SlugParams;                                  // extract movie slug from URL
  const [movie, setMovie] = useState<any|null>(null);
  const [showFullPlot, setShowFullPlot] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const fetchMovie = async () => {
      const { data, error } = await supabase
        .from('movies')
        .select('*')
        .eq('slug', slug)
        .maybeSingle();                                                       // fetch a single movie by slug

      if (error) {
        console.error('Error fetching movie:', error);
      } 

       if (!data) {
      setMovie(null);
      return;
      }

      setMovie(data);

    };

    fetchMovie();
  }, [slug]);                                                                 // re-run if the slug changes

  if (!movie) return;

  return (
    <div className="mt-5 mb-5 bg-background max-w-10xl mx-auto rounded-lg shadow-md">
      <div className="fixed top-4 left-22 w-8 h-8 mb-5">
        <button onClick={() => router.push("/")} className="text-l text-gray-800 flex items-center justify-center w-8 h-8 rounded-full bg-box hover:bg-highlight hover:cursor-pointer">
          <FaArrowLeftLong/>
        </button>
      </div>
      
      <div className="flex gap-9">
        <div className="relative group w-50 h-70 -mr-3">
          {movie.poster_filename && (
          <>
            <img
              src={`https://qivcmhdrljwmpwujkwqd.supabase.co/storage/v1/object/public/Wiki_Images/wikipedia_images/${movie.poster_filename}`}
              alt={movie.title}
              className="w-50 h-70 object-cover rounded-md bg-box/95"
            />
            <div className="absolute inset-0 bg-gray-900/50 opacity-0 group-hover:opacity-100 transition rounded-md" />
            <div className="absolute bottom-2 right-2 opacity-0 group-hover:opacity-100 transition">
              <LikeButton/>
            </div>
          </>
          )}
        </div>

      <div className="max-w-3xl flex bg-box/95 border rounded-lg px-5 py-5">
        <div className="flex flex-col">
          
          <h1 className="text-3xl font-bold mb-3">
            {movie.title}
          </h1>

          {/* <div className="text-sm text-text-dark mb-2 flex flex-wrap gap-5 items-center">
            <span className="bg-box border border-gray-400 rounded-full px-2 py-0.5 text-xs backdrop-blur-sm hover:bg-highlight hover:border-background hover:scale-[1.02]">
              {movie.genre}
            </span>
            <span className="bg-box border border-gray-400 rounded-full px-2 py-0.5 text-xs backdrop-blur-sm hover:bg-highlight hover:border-background hover:scale-[1.02]">
              {movie.releaseDate}
            </span>
          </div> */}

          <div className="text-sm text-text-dark mb-2 flex flex-wrap gap-5 items-center">
            {movie.genre && (
              <span className="bg-box border border-gray-400 rounded-full px-2 py-0.5 text-xs backdrop-blur-sm hover:bg-highlight hover:border-background hover:scale-[1.02]">
                {movie.genre}
              </span>
            )}

            {movie.releaseDate && (
              <span className="bg-box border border-gray-400 rounded-full px-2 py-0.5 text-xs backdrop-blur-sm hover:bg-highlight hover:border-background hover:scale-[1.02]">
                {movie.releaseDate}
              </span>
            )}
          </div>

          <div className="text-sm leading-relaxed">
            <p className={`${!showFullPlot ? 'line-clamp-3' : ''}`}>
              {movie.plot}
            </p>
            {movie.plot.length > 150 && (<button onClick={() => setShowFullPlot(!showFullPlot)} className="text-sm text-blue-500 mt-1 hover:underline hover:cursor-pointer">
                {showFullPlot ? 'Read less' : 'Read more'}
              </button>
            )}
          </div>

          <div className="text-sm text-text-dark mt-3 flex flex-wrap gap-2 items-center">
            {/* <span className="bg-box border border-gray-400 rounded-full px-2 py-0.5 text-xs backdrop-blur-sm hover:bg-highlight hover:border-background hover:scale-[1.02]">
              Directed By: {movie.director}
            </span> */}
              {movie.director && (
                <div className="text-sm text-text-dark flex flex-wrap gap-2 items-center">
                  <span className="bg-box border border-gray-400 rounded-full px-2 py-0.5 text-xs backdrop-blur-sm hover:bg-highlight hover:border-background hover:scale-[1.02]">
                    Directed By: {movie.director}
                  </span>
                </div>
              )}
            
          </div>

          <div className="text-sm text-text-dark mt-3 flex flex-wrap gap-2 items-center">
            {/* <span className="bg-box border border-gray-400 rounded-full px-2 py-0.5 text-xs backdrop-blur-sm hover:bg-highlight hover:border-background hover:scale-[1.01]">
              Featuring: {movie.cast}
            </span> */}

            {movie.cast && (
              <div className="text-sm text-text-dark flex flex-wrap gap-2 items-center">
                <span className="bg-box border border-gray-400 rounded-full px-2 py-0.5 text-xs backdrop-blur-sm hover:bg-highlight hover:border-background hover:scale-[1.01]">
                  Featuring: {movie.cast}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>
      </div>

      {/* <div className="flex gap-6 flex-wrap justify-center mt-5">
        <div className="w-45 h-65 bg-box/95 border rounded-md shadow transition-transform duration-300 hover:scale-102 hover:cursor-pointer"></div>
        <div className="w-45 h-65 bg-box/95 border rounded-md shadow transition-transform duration-300 hover:scale-102 hover:cursor-pointer"></div>
        <div className="w-45 h-65 bg-box/95 border rounded-md shadow transition-transform duration-300 hover:scale-102 hover:cursor-pointer"></div>
        <div className="w-45 h-65 bg-box/95 border rounded-md shadow transition-transform duration-300 hover:scale-102 hover:cursor-pointer"></div>
        <div className="w-45 h-65 bg-box/95 border rounded-md shadow transition-transform duration-300 hover:scale-102 hover:cursor-pointer"></div>
      </div> */}
      <MovieRec/>

    </div>
  );
}