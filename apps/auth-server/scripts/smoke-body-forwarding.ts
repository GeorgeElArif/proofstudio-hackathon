import { readFile } from "node:fs/promises";
import { join } from "node:path";

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) {
    throw new Error(message);
  }
}

const serverSource = await readFile(join(process.cwd(), "src/server.ts"), "utf8");

assert(
  /if \(method === "GET" \|\| method === "HEAD"\) \{\s*return new Request\(url, \{ method, headers \}\);\s*\}/s.test(serverSource),
  "GET/HEAD request conversion must omit a body.",
);
assert(
  /body:\s*Readable\.toWeb\(request\) as RequestInit\["body"\]/.test(serverSource),
  "Non-GET/non-HEAD request conversion must forward the IncomingMessage body.",
);
assert(
  /duplex:\s*"half"/.test(serverSource),
  "Streaming request bodies must set duplex half for Node fetch Request compatibility.",
);
assert(
  /headers\.(append|set)\(key,/.test(serverSource),
  "Request conversion must preserve forwarded headers.",
);

console.log("PS-040E auth-server POST body forwarding smoke passed.");
