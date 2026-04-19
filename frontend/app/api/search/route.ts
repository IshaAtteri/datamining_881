// api for routing to movie slug based on user's search

export async function GET() {
  return new Response(JSON.stringify({error: "Use Supabase queries directly - We don't use this endpoint anymore."}), {
    status: 410,
    headers: {"Content-Type": "application/json"},
  });
}