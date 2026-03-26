import movies from "../../../../movies.json";                             // import JSON dataset containing all movies 
export const dynamicParams = true;                                        // allow dynamic parameters, allows pages to be generated for any slug

export default async function page({params}: {params: any}) {
  const { slug } = await params;                                          // extract movie slug from URL
  const movie = movies.find((m) => m.slug?.trim() === slug?.trim());      // search movies array for movie whose slug matches 

  if (!movie) return <p>Movie not found</p>;

  return (
    <div className="mt-10 mb-10 bg-background max-w-4xl mx-auto rounded-lg shadow-md">
      <div className="flex gap-11">
        {movie.poster && (
        <img
          src={movie.poster}
          alt={movie.title}
          className="w-40 h-60 object-cover rounded-md bg-box/95"
        />
      )}
      
      <div className="max-w-2xl flex bg-box/95 border rounded-lg px-5 py-5">
        <div className="flex flex-col">
          
          <h1 className="text-3xl font-bold mb-3">
            {movie.title}
          </h1>

          <div className="text-sm text-text-dark mb-2 flex flex-wrap gap-3 items-center">
            <span className="bg-box border border-gray-400 rounded-full px-2 py-0.5 text-xs backdrop-blur-sm hover:bg-blue-500/20 hover:border-blue-400 hover:scale-[1.02]">
              {movie.genre}
            </span>
            <span className="bg-box border border-gray-400 rounded-full px-2 py-0.5 text-xs backdrop-blur-sm hover:bg-blue-500/20 hover:border-blue-400 hover:scale-[1.02]">
              {movie.releaseDate}
            </span>
          </div>

          <p className="text-sm leading-relaxed line-clamp-3">
            {movie.plot}
          </p>

          <div className="text-sm text-text-dark mt-2 flex flex-wrap gap-3 items-center">
            <span className="bg-box border border-gray-400 rounded-full px-2 py-0.5 text-xs backdrop-blur-sm hover:bg-blue-500/20 hover:border-blue-400 hover:scale-[1.02]">
              Directed By: {movie.director}
            </span>
          </div>

          <div className="text-sm text-text-dark mt-2 flex flex-wrap gap-3 items-center">
            <span className="bg-box border border-gray-400 rounded-full px-2 py-0.5 text-xs backdrop-blur-sm hover:bg-blue-500/20 hover:border-blue-400 hover:scale-[1.01]">
              Featuring: {movie.cast}
            </span>
          </div>
        </div>
      </div>
      </div>

      <div className="flex gap-5 flex-wrap justify-center mt-5">
        <div className="w-40 h-60 bg-box/95 border rounded-md shadow transition-transform duration-300 hover:scale-102 hover:cursor-pointer"></div>
        <div className="w-40 h-60 bg-box/95 border rounded-md shadow transition-transform duration-300 hover:scale-102 hover:cursor-pointer"></div>
        <div className="w-40 h-60 bg-box/95 border rounded-md shadow transition-transform duration-300 hover:scale-102 hover:cursor-pointer"></div>
        <div className="w-40 h-60 bg-box/95 border rounded-md shadow transition-transform duration-300 hover:scale-102 hover:cursor-pointer"></div>
        <div className="w-40 h-60 bg-box/95 border rounded-md shadow transition-transform duration-300 hover:scale-102 hover:cursor-pointer"></div>
      </div>

    </div>
  );
}