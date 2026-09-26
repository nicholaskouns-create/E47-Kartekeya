import { installCityPulse } from "./city-pulse.js";

export const CITY_QUERY_SCHEMA = "CITY-QUERY/1.0";

export function makeCityQuery({
  query_code,
  title = "City query",
  prompt,
  task_type = "general",
  observations = [],
  requested_sources = [],
  blind_sources = [],
  metadata = {},
} = {}) {
  if (!query_code || !prompt) throw new Error("query_code and prompt are required");
  return {
    schema: CITY_QUERY_SCHEMA,
    query_code,
    title,
    prompt,
    task_type,
    observations,
    requested_sources,
    blind_sources,
    metadata,
    created_at: new Date().toISOString(),
  };
}

export function installCityQuery({ surface = "CITY", onQuery = null } = {}) {
  const pulse = installCityPulse({
    surface,
    onPulse(packet) {
      const query = packet?.query_packet;
      if (!query || query.schema !== CITY_QUERY_SCHEMA) return;
      window.CITY_QUERY_STATE = query;
      document.dispatchEvent(new CustomEvent("city:query", { detail: query }));
      onQuery?.(query, packet);
    },
  });

  function publish(query) {
    if (!query || query.schema !== CITY_QUERY_SCHEMA) {
      throw new Error("CITY_QUERY contract violation");
    }
    return pulse.publish({
      run_id: query.query_code,
      t: Date.now() / 1000,
      carrier: 125,
      e47: 47,
      state: "query",
      evidence_class: "E1",
      query_packet: query,
    });
  }

  const api = { schema: CITY_QUERY_SCHEMA, surface, publish, pulse };
  window.CITY_QUERY = api;
  return api;
}
