import http from "k6/http";
import { check, sleep } from "k6";
export const options = { vus: 10, duration: "20s" };
export default function () {
  const url = __ENV.GW_URL || "http://127.0.0.1:8080/health";
  const res = http.get(url);
  check(res, { "status is 200": (r) => r.status === 200 });
  sleep(0.2);
}
