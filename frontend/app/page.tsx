"use client";                                                                         // needed for client-specific features like interactivity, state, event handlers 

import {useState, useEffect, useRef} from "react";
import {useRouter} from "next/navigation";
import {supabase} from '../lib/supabase';                                             // import Supabase client 

import Likes from "../components/Likes";
import Recs from "../components/Recs";

type movie = {                                                                        // define TypeScript type for movie
  title: string;
  slug?: string;
  poster?: string | null;
};

export default function Home() {
  const [search, setSearch] = useState("");         
  const [error, setError] = useState("");    
  const [moviesList, setMoviesList] = useState<any[]>([]);
  const router = useRouter();                                                         // router object for navigating to other pages  

  useEffect(() => {                                                                   // fetch movie data on page load
    const fetchMovies = async () => {
      const {data, error} = await supabase.from('movies').select('*').limit(6);       // currently limit to 6 movies

      if (error) {
        console.error('Error fetching movie list:', error);
        return;
      }

      setMoviesList(data);                                                            // store movies in state
    };

    fetchMovies();
  }, []);

  const userSearch = async (e: any) => {                                              // handles form submission - must be async for await to work (await = pauses until JSON parsing is complete!)
    e.preventDefault();                                                               // prevent default form submission (page reloading)

    if (!search.trim()) return;                                                       // if search is empty don't do anything 

      try {
        const {data, error} = await supabase.from('movies').select('*').ilike('title', `%${search}%`);  // use 'ilike' for case-insensitive matching of 'title' col

        if (error) {
          setError('Error fetching movies');
          console.error(error);
          return;
        }

        if (data && data.length > 0) {                                                // if movie found and has slug, navigate to first movie's detail page 
          router.push(`/movie/${data[0].slug}`);
        } else 
          setError('Movie not found');
      } catch (err) {
        setError('Error fetching movies');
        console.error(err);
      }

      // try {
      //   const res = await fetch(`/api/search?q=${encodeURIComponent(search)}`);
      //   const movies: movie[] = await res.json();         // convert HTTP response from JSON into JS array of movie objects

      //   if (movies.length > 0 && movies[0].slug)          // if at least one movie is returned from API and first movie has a slug defined
      //     router.push(`/movie/${movies[0].slug}`);        // then navigate user to movie detail page using slug of first movie in results
      //   else
      //     setError("Movie not found");                    // if no movies were returned or first movie has no slug, show error message
      // }
      // catch (err) 
      // {
      //   setError("Error fetching movies");
      //   console.error(err);
      // }
  };

  return (
    <div className="flex flex-col flex-1 items-center justify-center bg-background font-sans">
      <main className="flex flex-1 w-full max-w-5xl flex-col items-center justify-between py-12 sm:items-start">
        <form onSubmit={userSearch} className="flex gap-2">
        <div className="relative">
          <input
            type="text"
            placeholder="Search for a movie..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);                                              // update search text as user types
              setError("");                                                           // clear error when user starts typing 
            }}
            className="px-4 py-2 border rounded bg-box w-230"
          />
          {search && (                                                                // clear button 
            <button type="button" onClick={() => setSearch("")} className="absolute right-2 -top-2 mr-2 h-full flex items-center justify-center text-gray-500 hover:cursor-pointer">
              ✕
            </button>
          )}
          </div>
          <button type="submit" className="px-4 py-2 mb-5 bg-button text-text-light border-button rounded hover:cursor-pointer"> 
            Search
          </button>
        </form>

        <Likes/>

        <Recs/>

      </main>
    </div>
  );
}