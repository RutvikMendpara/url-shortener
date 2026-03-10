import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  vus: 1,
  iterations: 12, // go slightly above rate limit
};

export default function () {
  const payload = JSON.stringify({
    original_url: "https://example.com",
  });

  const params = {
    headers: {
      "Content-Type": "application/json",
    },
  };

  const res = http.post("http://localhost:8000/url/shorten", payload, params);

  check(res, {
    "created or rate limited": (r) =>
      r.status === 200 || r.status === 201 || r.status === 429,
  });

  sleep(1);
}
