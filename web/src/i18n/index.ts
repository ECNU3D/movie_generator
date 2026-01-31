import zhMessages from "./messages/zh.json";
import enMessages from "./messages/en.json";

export type Locale = "zh" | "en";

export type Messages = typeof zhMessages;

const messages: Record<Locale, Messages> = {
  zh: zhMessages,
  en: enMessages,
};

export function getMessages(locale: Locale): Messages {
  return messages[locale];
}

// Type-safe translation key path
type PathsToStringProps<T> = T extends string
  ? []
  : {
      [K in Extract<keyof T, string>]: [K, ...PathsToStringProps<T[K]>];
    }[Extract<keyof T, string>];

type Join<T extends string[], D extends string> = T extends []
  ? never
  : T extends [infer F]
  ? F
  : T extends [infer F, ...infer R]
  ? F extends string
    ? `${F}${D}${Join<Extract<R, string[]>, D>}`
    : never
  : string;

export type TranslationKey = Join<PathsToStringProps<Messages>, ".">;

// Get nested value from object by dot-separated path
function getNestedValue(obj: Record<string, unknown>, path: string): string {
  const keys = path.split(".");
  let result: unknown = obj;

  for (const key of keys) {
    if (result && typeof result === "object" && key in result) {
      result = (result as Record<string, unknown>)[key];
    } else {
      return path; // Return key if not found
    }
  }

  return typeof result === "string" ? result : path;
}

// Translation function
export function createTranslator(locale: Locale) {
  const msgs = getMessages(locale);

  return function t(key: string, params?: Record<string, string | number>): string {
    let value = getNestedValue(msgs as unknown as Record<string, unknown>, key);

    // Replace parameters like {name} with actual values
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        value = value.replace(new RegExp(`\\{${k}\\}`, "g"), String(v));
      });
    }

    return value;
  };
}

export { zhMessages, enMessages };
