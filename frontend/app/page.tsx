"use client";                                       // needed for client-specific features like interactivity, state, event handlers 

import {useState} from "react";
import {useRouter} from "next/navigation";
// import movies from "../../movies.json";          // import JSON dataset containing all movies 

type movie = {                                      // define TypeScript type for a movie
  title: string;
  slug?: string;
  poster?: string | null;
};

export default function Home() {
  const [search, setSearch] = useState("");         
  const [error, setError] = useState("");         
  const router = useRouter();                       // router object for navigating to other pages        

  const userSearch = async (e: any) => {            // must be async for await to work (await = pauses until JSON parsing is complete!)
    e.preventDefault();                             // prevent default form submission (page reloading)

    if (!search.trim()) return;

      try {
        const res = await fetch(`/api/search?q=${encodeURIComponent(search)}`);
        const movies: movie[] = await res.json();   // convert HTTP response from JSON into JS array of movie objects

        if (movies.length > 0 && movies[0].slug)    // if at least one movie is returned from API and first movie has a slug defined
          router.push(`/movie/${movies[0].slug}`);  // then navigate user to movie detail page using slug of first movie in results
        else
          setError("Movie not found");              // if no movies were returned or first movie has no slug, show error message
      }
      catch (err) 
      {
        setError("Error fetching movies");
        console.error(err);
      }
  };

  return (
    <div className="flex flex-col flex-1 items-center justify-center bg-background font-sans">
      <main className="flex flex-1 w-full max-w-3xl flex-col items-center justify-between py-32 sm:items-start">
        <form onSubmit={userSearch} className="flex gap-2">
          <input
            type="text"
            placeholder="Search for a movie..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);            // update search text as user types
              setError("");                         // clear error when user starts typing 
            }}
            className="px-4 py-2 border rounded bg-box w-180">
          </input>
          <button type = "submit" className="px-4 py-2 bg-button text-text-light border rounded hover:cursor-pointer hover:bg-[var(--button-dark)]"> 
            Search
          </button>
        </form>
      </main>
    </div>
  );
}