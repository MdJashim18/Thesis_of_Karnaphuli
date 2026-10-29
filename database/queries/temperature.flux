
from(bucket: "tunnel_telemetry")
  |> range(start: -1h)
  |> filter(fn: (r) => r._field == "temperature")
