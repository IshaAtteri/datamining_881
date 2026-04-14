"use client";

import {useEffect, useState} from "react";
import {supabase} from '../lib/supabase';                                                   // supabase client

import ExpandMovie from "../components/ExpandMovie";
import MovieCard from "../components/MovieCard";

type movieRecParam = {
  querySlug: string;                                                                        // querySlug = slug of searched movie
  method: "algo" | "model";                                                                 // decides which method to use for recommendation system
};

type movieRec = {
  // slug: string;
  // score: number;
  // title?: string;             
  // poster_filename?: string;   
  slug: string;
  score: number;
  title?: string;
  poster_filename?: string;
  plot?: string;
  genre?: string[];
  release_date?: string;
  cast?: string[];
  director?: string;
};


export default function MovieRec({querySlug, method}: movieRecParam) {
  const [recommendations, setRecommendations] = useState<movieRec[]>([]);
  const [expandedSlug, setExpandedSlug] = useState<string | null>(null);

  const toggleMovie = (slug: string) => {setExpandedSlug((prev) => (prev === slug ? null : slug));};
  const expandedMovie = recommendations.find((m) => m.slug === expandedSlug);

  useEffect(() => {
    if (expandedSlug) {
      const element = document.getElementById(`movie-${expandedSlug}`);
      element?.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
    }
  }, [expandedSlug]);

  useEffect(() => {
    if (!querySlug) return;                                                                 

    const fetchRecs = async () => {
      try {
        // const res = await fetch("http://localhost:8000/predict",                            // fetch top recommendations from API
        // {
        //   method: "POST",
        //   headers: {"Content-Type": "application/json"},
        //   body: JSON.stringify({query_slug: querySlug}),
        // });

        const endpoint = method === "model" ? "http://localhost:8000/predict/model": "http://localhost:8000/predict/algorithm";
        const res = await fetch(endpoint, 
          {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(method === "model"
              ? { query_slug: querySlug }
              : { query_slugs: [querySlug] }), // The backend now supports a list for the algorithm endpoint, so even for a single movie, it should be passed in as a list
          });

        const data: movieRec[] = await res.json();
        const top5 = data.slice(0, 5);

        const {data: moviesData, error} = await supabase                                    // fetch movie titles and poster filenames from Supabase
          .from("movies")
          // .select("slug, title, poster_filename")
          .select("slug, title, poster_filename, plot, genre, release_date, cast, director")
          .in("slug", top5.map((r) => r.slug));

        const movieMap = Object.fromEntries((moviesData || []).map((m) => [m.slug, m]));    // create lookup map from slug --> movie data

        // const withTitles = top5.map((rec) => ({                                             // combine API and Supabase results 
        //   ...rec,
        //   title: movieMap[rec.slug]?.title || rec.slug,
        //   poster_filename: movieMap[rec.slug]?.poster_filename || "",
        // }));

        const withMetadata = top5.map((rec) => ({
          ...rec,
          title: movieMap[rec.slug]?.title || rec.slug,
          poster_filename: movieMap[rec.slug]?.poster_filename || "",
          plot: movieMap[rec.slug]?.plot || "",
          genre: movieMap[rec.slug]?.genre || [],
          release_date: movieMap[rec.slug]?.release_date || "",
          cast: movieMap[rec.slug]?.cast || [],
          director: movieMap[rec.slug]?.director || "",
        }));

        // setRecommendations(withTitles);
        setRecommendations(withMetadata);

      } catch (err) {
        console.error("Error fetching recommendations:", err);
      }
    };

    fetchRecs();
  }, [querySlug, method]);

   if (!recommendations.length) {                                                           // placeholder cards to maintain layout
    return (
      <div className="flex gap-6 flex-wrap justify-center mt-5">
        {Array.from({length: 5}).map((_, idx) => (<div key={idx} className="w-45 h-65 bg-box/95 border rounded-md shadow transition-transform duration-300 hover:scale-102 hover:cursor-pointer"></div>))}
      </div>
    );
  }

return (
  <div className="flex flex-col gap-6 mt-5">
    <div className="flex gap-6 flex-wrap justify-center">
      {recommendations.map((rec) => {
        const isSelected = expandedSlug === rec.slug;
        const isDimmed = expandedSlug && !isSelected;

        return (
          <div key={rec.slug} id={`movie-${rec.slug}`} className={`relative group w-45 h-65 bg-box/95 border rounded-md shadow transition-all duration-300 overflow-hidden
              ${isSelected ? "scale-105 z-20 ring-2 ring-white" : isDimmed ? "opacity-40" : "hover:scale-102"}`}>

              <img
                src={`https://qivcmhdrljwmpwujkwqd.supabase.co/storage/v1/object/public/Wiki_Images/wikipedia_images/${rec.poster_filename}`}
                className="w-full h-full object-cover"
              />

            <div className="absolute inset-0 bg-gray-900/50 opacity-0 group-hover:opacity-100 transition rounded-md" />

            <div className="absolute bottom-0 w-full bg-black/60 text-white text-sm p-1 text-center">
              {(rec.title || rec.slug).replace(/\([^)]*\bfilm\b[^)]*\)/gi, "")}
            </div>

            <div className="absolute bottom-2 right-2 z-10">
              <ExpandMovie onClick={() => toggleMovie(rec.slug)} isOpen={expandedSlug === rec.slug}/>
            </div>

          </div>
        );
      })}

    </div>

    {expandedMovie && (
      <div className="w-full flex justify-center animate-slideDown">
          <div className="w-full max-w-5xl bg-box rounded-xl p-2 overflow-hidden bg-highlight">
            <MovieCard movie = {expandedMovie}/>
          </div>
        </div>
      )}

    </div>
  );
}