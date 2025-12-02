from collections.abc import Mapping, Sequence

type JSONPrimitive = str | int | float | bool | None

# Forward reference com string para permitir recursão
type JSONValue = JSONPrimitive | JSONArray | JSONObject

type JSONObject = Mapping[str, JSONValue]
type JSONArray = Sequence[JSONValue]
