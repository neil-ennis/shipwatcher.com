export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // Preserve WordPress's published /?p=123 shortlinks after the site
    // becomes static. Cloudflare's _redirects cannot match query strings.
    if (url.pathname === "/" && /^\d+$/.test(url.searchParams.get("p") || "")) {
      const mapResponse = await env.ASSETS.fetch(new URL("/postmap.json", url));
      if (!mapResponse.ok) return new Response("Shortlink map unavailable", { status: 503 });
      const postMap = await mapResponse.json();
      const destination = postMap[url.searchParams.get("p")];
      if (destination) return Response.redirect(new URL(destination, url), 301);
    }

    return env.ASSETS.fetch(request);
  },
};
