import http from "k6/http";
import { sleep, check } from "k6";

export const options = {
  vus: 50,
  duration: "30s",
};

export default function () {
  const res = http.get("http://localhost:8000/url/3", {
    redirects: 0,
  });

  check(res, {
    "is redirect": (r) => r.status === 307 || r.status === 302,
  });

  sleep(1);
}
