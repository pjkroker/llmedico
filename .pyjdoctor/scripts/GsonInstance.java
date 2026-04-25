package org.toradocu.util;

import com.google.gson.*;
import org.toradocu.output.util.JsonOutput;
import org.toradocu.output.util.JsonOutputSerializer;
import java.lang.reflect.Type;

/** This class holds an instance of a {@code Gson} object. */
public final class GsonInstance {

  /** The Gson object instance. */
  private static final Gson gson = buildGson();

  /** Builds a Gson instance with all necessary adapters registered. */
  private static Gson buildGson() {
    // Adapter for Class<?>: serializes it as its fully qualified name
    JsonSerializer<Class<?>> classSerializer = new JsonSerializer<Class<?>>() {
      @Override
      public JsonElement serialize(Class<?> src, Type typeOfSrc, JsonSerializationContext context) {
        return new JsonPrimitive(src == null ? null : src.getName());
      }
    };

    JsonDeserializer<Class<?>> classDeserializer = new JsonDeserializer<Class<?>>() {
      @Override
      public Class<?> deserialize(JsonElement json, Type typeOfT, JsonDeserializationContext context)
          throws JsonParseException {
        try {
          String name = json.getAsString();
          return name == null ? null : Class.forName(name);
        } catch (ClassNotFoundException e) {
          throw new JsonParseException(e);
        }
      }
    };

    return new GsonBuilder()
        .registerTypeAdapter(JsonOutput.class, new JsonOutputSerializer())
        .registerTypeAdapter(Class.class, classSerializer)
        .registerTypeAdapter(Class.class, classDeserializer)
        .disableHtmlEscaping()
        .setPrettyPrinting()
        .create();
  }

  /** Disables construction of this class. */
  private GsonInstance() {}

  /**
   * Returns the Gson instance held by this class.
   *
   * @return the Gson instance held by this class
   */
  public static Gson gson() {
    return gson;
  }
}