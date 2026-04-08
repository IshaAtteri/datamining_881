"use client";

import {useEffect, useState} from "react";
import {supabase} from '../lib/supabase';                                                   // supabase client

type movieRecParam = {
  querySlug: string;                                                                        // querySlug = slug of searched movie
};

type movieRec = {
  slug: string;
  score: number;
  title?: string;             
  poster_filename?: string;   
};

export default function MovieRec({querySlug}: movieRecParam) {
  const [recommendations, setRecommendations] = useState<movieRec[]>([]);
  
  useEffect(() => {
    if (!querySlug) return;                                                                 

    const fetchRecs = async () => {
      try {
        const res = await fetch("http://localhost:8000/predict",                            // fetch top recommendations from API
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({query_slug: querySlug}),
        });

        const data: movieRec[] = await res.json();
        const top5 = data.slice(0, 5);

        const {data: moviesData, error} = await supabase                                    // fetch movie titles and poster filenames from Supabase
          .from("movies")
          .select("slug, title, poster_filename")
          .in("slug", top5.map((r) => r.slug));

        const movieMap = Object.fromEntries((moviesData || []).map((m) => [m.slug, m]));    // create lookup map from slug --> movie data

        const withTitles = top5.map((rec) => ({                                             // combine API and Supabase results 
          ...rec,
          title: movieMap[rec.slug]?.title || rec.slug,
          poster_filename: movieMap[rec.slug]?.poster_filename || "",
        }));

        setRecommendations(withTitles);

      } catch (err) {
        console.error("Error fetching recommendations:", err);
      }
    };

    fetchRecs();
  }, [querySlug]);

   if (!recommendations.length) {                                                           // placeholder cards to maintain layout
    return (
      <div className="flex gap-6 flex-wrap justify-center mt-5">
        {Array.from({length: 5}).map((_, idx) => (<div key={idx} className="w-45 h-65 bg-box/95 border rounded-md shadow transition-transform duration-300 hover:scale-102 hover:cursor-pointer"></div>))}
      </div>
    );
  }

  return (
    <div className="flex gap-6 flex-wrap justify-center mt-5">
      {recommendations.map((rec) => (
        <div key={rec.slug} className="w-45 h-65 bg-box/95 border rounded-md shadow transition-transform duration-300 hover:scale-102 hover:cursor-pointer overflow-hidden relative">
          {rec.poster_filename && (
            <img
              src={`https://qivcmhdrljwmpwujkwqd.supabase.co/storage/v1/object/public/Wiki_Images/wikipedia_images/${rec.poster_filename}`}
              alt={rec.title || rec.slug}
              className="w-full h-full object-cover"
            />
          )}
          <div className="absolute bottom-0 left-0 w-full bg-black/50 text-white text-sm p-1 text-center">
            {rec.title || rec.slug}
          </div>
        </div>
      ))}
    </div>
  );
}