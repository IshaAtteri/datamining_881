import movies from "../../../../movies.json";                             // import JSON dataset containing all movies 

export async function GET(req: Request) {
  const {searchParams} = new URL(req.url);                                // gets request URL w/ query parameters
  const query = searchParams.get("q")?.toLowerCase() || "";

  const results = movies                                                  // only return movies that include search term in their title
    .filter((m) => m.title.toLowerCase().includes(query))                 // filter searches dataset for titles containing query
    .slice(0, 10);                                                        // limit to top 10 results

  return new Response(JSON.stringify(results), {
    headers: {"Content-Type": "application/json"},                        // returns JSON array of movie objects
  });
}