// import movies from "../../../../movies.json";                            // import JSON dataset containing all movies 

"use client";                                                               // needed for client-specific features like interactivity, state, event handlers 

import {supabase} from '../../../lib/supabase';                             // import Supabase client
import {use, useEffect, useState} from 'react';
import {useRouter} from "next/navigation";                                  // import this for back button

import MovieRec from "../../../components/MovieRec";
import LikeButton from "../../../components/LikeButton";
import Toggle from "../../../components/Toggle";

import {FaArrowLeftLong} from "react-icons/fa6";

export const dynamicParams = true;                                          // allow dynamic parameters, allows pages to be generated for any slug

type SlugParams = {slug: string};

export default function Page({params}: {params: any}) {
  const {slug} = use(params) as SlugParams;                                  // extract movie slug from URL
  const [movie, setMovie] = useState<any|null>(null);
  const [showFullPlot, setShowFullPlot] = useState(false);
  const [recMethod, setRecMethod] = useState<"algo"|"model">("algo");
  const router = useRouter();

  useEffect(() => {
    const fetchMovie = async () => {
      const {data, error} = await supabase
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
      <div className="fixed top-4 left-10 z-50 flex items-center gap-3">
        <button onClick={() => router.push("/")} className="text-l text-gray-800 flex items-center justify-center w-6 h-6 rounded-full bg-box hover:bg-highlight hover:cursor-pointer hover:text-white">
          <FaArrowLeftLong className="text-xs"/>
        </button>
        <Toggle selected = {recMethod} onChange = {setRecMethod}/>
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

      <div className="max-w-3xl flex bg-highlight/85 border rounded-xl px-2 py-2">
      <div className="max-w-3xl flex bg-box rounded-lg px-5 py-5">
        <div className="flex flex-col">
          
          <h1 className="text-3xl font-bold mb-2 -mt-1">
            {/* {movie.title} */}
            {movie.title.replace(/\([^)]*\bfilm\b[^)]*\)/gi, '')}
            {/* \( and \) matches parentheses,  [^)]* refers to anything inside parentheses, \bfilm\b makes sure the word film is present, gi makes it case-insensitive, wrap in / / for syntax purposes*/}
          </h1>

          <div className="text-sm text-text-dark mb-2 flex flex-wrap gap-5 items-center">
            {movie.pre_genre && (
              <span className="bg-gray-200/50 border-2 border-background/60 rounded-full px-2 py-0.5 text-xs backdrop-blur-sm hover:bg-highlight/60 hover:border-background hover:scale-[1.02]">
                {movie.pre_genre}
              </span>
            )}

            {movie.releaseDate && (
              <span className="bg-gray-200/50 border-2 border-background/60 rounded-full px-2 py-0.5 text-xs backdrop-blur-sm hover:bg-highlight/60 hover:border-background hover:scale-[1.02]">
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
              {movie.director && (
                <div className="text-sm text-text-dark flex flex-wrap gap-2 items-center">
                  <span className="bg-gray-200/50 border-2 border-background/60 rounded-full px-2 py-0.5 text-xs backdrop-blur-sm hover:bg-highlight/60 hover:border-background hover:scale-[1.02]">
                    Directed By: {movie.director}
                  </span>
                </div>
              )}
            
          </div>

          <div className="text-sm text-text-dark mt-3 flex flex-wrap gap-2 items-center">
            {movie.cast && (
              <div className="text-sm text-text-dark flex flex-wrap gap-2 items-center">
                <span className="bg-gray-200/50 border-2 border-background/60 rounded-full px-2 py-0.5 text-xs backdrop-blur-sm hover:bg-highlight/60 hover:border-background hover:scale-[1.01]">
                  Featuring: {movie.cast}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>
      </div>
      </div>
      
      <MovieRec querySlug = {movie.slug} method = {recMethod}/>
    </div>
  );
}