from collections.abc import Mapping, Sequence
from uuid import UUID

type JSONPrimitive = str | int | float | bool | None

# Forward reference com string para permitir recursão
type JSONValue = JSONPrimitive | JSONArray | JSONObject

type JSONObject = Mapping[str, JSONValue]
type JSONArray = Sequence[JSONValue]

# Realtime types
type Event = str
type ClientID = UUID
type SID = str
