import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { extname, join, normalize } from "node:path";

const root = join(process.cwd(), "static");
const port = Number(process.env.PORT || 5173);
const cubeTargets = [
  process.env.CUBE_API_PROXY_URL,
  "http://cube:4000",
  "http://localhost:4000"
].filter(Boolean);

const contentTypes = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "application/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8"
};

createServer(async (request, response) => {
  const url = new URL(request.url || "/", `http://${request.headers.host}`);

  if (url.pathname.startsWith("/cubejs-api/")) {
    for (const target of cubeTargets) {
      try {
        const upstream = await fetch(new URL(url.pathname + url.search, target), {
          method: request.method,
          headers: {
            "content-type": request.headers["content-type"] || "application/json",
            ...(request.headers.authorization ? { authorization: request.headers.authorization } : {})
          },
          body: request.method === "GET" || request.method === "HEAD" ? undefined : request,
          duplex: "half"
        });

        response.writeHead(upstream.status, {
          "Content-Type": upstream.headers.get("content-type") || "application/json",
          "Cache-Control": "no-store"
        });
        response.end(Buffer.from(await upstream.arrayBuffer()));
        return;
      } catch {
        // Try the next configured Cube target.
      }
    }

    response.writeHead(502, { "Content-Type": "application/json; charset=utf-8" });
    response.end(JSON.stringify({ error: "Cube API is unavailable" }));
    return;
  }

  const requestedPath = url.pathname === "/" ? "/index.html" : url.pathname;
  const safePath = normalize(requestedPath).replace(/^(\.\.[/\\])+/, "");
  const filePath = join(root, safePath);

  try {
    const body = await readFile(filePath);
    response.writeHead(200, {
      "Content-Type": contentTypes[extname(filePath)] || "application/octet-stream",
      "Cache-Control": "no-store"
    });
    response.end(body);
  } catch {
    const fallback = await readFile(join(root, "index.html"));
    response.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
    response.end(fallback);
  }
}).listen(port, "0.0.0.0", () => {
  console.log(`Gallery analytics UI is available on http://0.0.0.0:${port}`);
});
