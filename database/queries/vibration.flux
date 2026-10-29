
from(bucket: "tunnel_telemetry")
  |> range(start: -1h)
  |> filter(fn: (r) =>
    r._field == "accel_x" or
    r._field == "accel_y" or
    r._field == "accel_z"
  )
