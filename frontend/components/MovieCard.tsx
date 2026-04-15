"use client";
import {useState} from "react";

type Movie = {
  slug: string;
  score?: number; 
  title?: string;
  poster_filename?: string;
  plot?: string;
  genre?: string[] | string;
  release_date?: string;
  cast?: string[] | string;
  director?: string;
};

type Params = {
  movie: Movie;
};

export default function MovieCard({movie}: Params) {
  const [showFullPlot, setShowFullPlot] = useState(false);
  const cast = Array.isArray(movie.cast) ? movie.cast : typeof movie.cast === "string" ? movie.cast.split(",") : [];
  const genre = Array.isArray(movie.genre) ? movie.genre : typeof movie.genre === "string"? movie.genre.split(",").map((g) => g.trim()) : [];

  return (
    <div className="bg-box rounded-lg flex flex-col gap-2 px-3 py-3"> 

      <h1 className="text-2xl font-bold">
        {movie.title?.replace(/\([^)]*\bfilm\b[^)]*\)/gi, "")}
      </h1>

      <div className="text-sm flex flex-wrap gap-2">
        {genre.map((g) => (<span key={g} className="px-2 py-0.5 bg-gray-200/50 rounded-full text-xs w-fit border-2 border-background/60 backdrop-blur-sm hover:bg-highlight/60 hover:border-background hover:scale-[1.01]">{g}</span>))}

        {movie.release_date && (
          <span className="px-2 py-0.5 bg-gray-200/50 rounded-full text-xs w-fit border-2 border-background/60 backdrop-blur-sm hover:bg-highlight/60 hover:border-background hover:scale-[1.01]">
            {movie.release_date?.match(/\d{4}/)?.[0]} 
            {/* directly extracts year */}
          </span>
        )}
      </div>

      {movie.plot && (
        <div className="text-sm leading-relaxed">
          <p className={!showFullPlot ? "line-clamp-3" : ""}>
            {movie.plot}
          </p>

          {movie.plot.length > 150 && (
            <button onClick={() => setShowFullPlot(!showFullPlot)} className="text-blue-500 mt-1 hover:underline text-sm">
              {showFullPlot ? "Read less" : "Read more"}
            </button>
          )}
        </div>
      )}

      {movie.director && (
        <span className="px-2 py-0.5 bg-gray-200/50 rounded-full text-xs w-fit border-2 border-background/60 backdrop-blur-sm hover:bg-highlight/60 hover:border-background hover:scale-[1.01]">
          Directed by: {movie.director}
        </span>
      )}

      {cast.length > 0 && (
        <span className="px-2 py-0.5 bg-gray-200/50 rounded-full text-xs w-fit border-2 border-background/60 backdrop-blur-sm hover:bg-highlight/60 hover:border-background hover:scale-[1.01]">
          Featuring: {cast.join(", ")}
        </span>
      )}
    </div>
  );
}