"use client";

import { create } from "zustand";

import type { ImageVersion, StoredImage, Style, StudioTab, View } from "@/features/creator/types";

type CreatorState = {
  view: View;
  prompt: string;
  style: Style;
  /** Photo attached in the prompt step; kept so going back or an error does not lose it. */
  photo: File | null;
  /** Every version of the image, oldest first: the original, then one per edit. */
  versions: ImageVersion[];
  /** The version shown in the studio, which the 3D model is built from. */
  currentImage: StoredImage | null;
  activeTab: StudioTab;
  modelId: string | null;
  /** When the 3D task started, for the elapsed time on the progress screen. */
  modelStartedAt: number | null;
  /** USD spent since the page was opened (sum of the costs Runware reports per call). */
  sessionSpend: number;

  setView: (view: View) => void;
  setPrompt: (prompt: string) => void;
  setStyle: (style: Style) => void;
  setPhoto: (photo: File | null) => void;
  setActiveTab: (tab: StudioTab) => void;
  /** A new starting image: drops the versions and the 3D model of the previous one. */
  startImage: (image: StoredImage) => void;
  addEdit: (image: StoredImage, instruction: string, sourceId: string) => void;
  /** Apply another version as the current image. Its 3D model no longer matches: drop it. */
  applyVersion: (image: StoredImage) => void;
  startModel: (modelId: string) => void;
  dropModel: () => void;
  addSpend: (value: number | null) => void;
  reset: () => void;
};

const initialState = {
  view: "create" as View,
  prompt: "",
  style: "free" as Style,
  photo: null,
  versions: [],
  currentImage: null,
  activeTab: "2d" as StudioTab,
  modelId: null,
  modelStartedAt: null,
  sessionSpend: 0,
};

const withoutModel = { modelId: null, modelStartedAt: null, activeTab: "2d" as StudioTab };

export const useCreatorStore = create<CreatorState>()((set) => ({
  ...initialState,

  setView: (view) => set({ view }),
  setPrompt: (prompt) => set({ prompt }),
  setStyle: (style) => set({ style }),
  setPhoto: (photo) => set({ photo }),
  setActiveTab: (activeTab) => set({ activeTab }),
  startImage: (image) =>
    set({
      ...withoutModel,
      versions: [{ image, instruction: null, sourceId: null }],
      currentImage: image,
    }),
  addEdit: (image, instruction, sourceId) =>
    set((state) => ({ versions: [...state.versions, { image, instruction, sourceId }] })),
  applyVersion: (image) => set({ ...withoutModel, currentImage: image }),
  startModel: (modelId) => set({ modelId, modelStartedAt: Date.now(), activeTab: "3d" }),
  dropModel: () => set(withoutModel),
  addSpend: (value) => {
    if (!value) return;
    set((state) => ({ sessionSpend: state.sessionSpend + value }));
  },
  // Spend survives a restart: it tracks the whole testing session.
  reset: () => set((state) => ({ ...initialState, sessionSpend: state.sessionSpend })),
}));
