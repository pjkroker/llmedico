package org.toradocu.output.util;

import com.google.gson.*;
import java.lang.reflect.*;

/** Created by arianna on 29/06/17. */
public class JsonOutputSerializer implements JsonSerializer<JsonOutput> {

  @Override
  public JsonElement serialize(
      JsonOutput src, java.lang.reflect.Type typeOfSrc, JsonSerializationContext context) {

    // --- FIX: create a Gson that knows how to serialize java.lang.Class objects ---
    Gson gson = new GsonBuilder()
        .registerTypeAdapter(
            Class.class,
            (JsonSerializer<Class<?>>)
                (clazz, t, ctx) ->
                    new JsonPrimitive(clazz == null ? null : clazz.getName()))
        .create();

    // Use that configured Gson to turn the object into a Json tree
    JsonObject jObj = (JsonObject) gson.toJsonTree(src);

    // Preserve existing logic
    if (src.containingClass.qualifiedName.equals(src.name)) {
      jObj.remove("returnType");
    }

    return jObj;
  }
}