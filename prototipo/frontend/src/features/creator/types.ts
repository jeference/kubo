export type StoredImage = {
  id: string;
  url: string;
  cost: number | null;
  warning: string;
};

export type ModelStatus = {
  id: string;
  status: "processing" | "success" | "error";
  glb_url: string;
  cost: number | null;
  error: string;
};

export type View = "create" | "studio";

export type StudioTab = "2d" | "3d";

export type Style = "free" | "pixar" | "mini-pop" | "chibi";

/** One image of the session: the original (no instruction) or the result of an edit. */
export type ImageVersion = {
  image: StoredImage;
  instruction: string | null;
  sourceId: string | null;
};

/** Runware account, in USD. */
export type Credits = {
  balance: number;
  total_spent: number;
};
