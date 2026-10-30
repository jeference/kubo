"use client";

import { create } from "zustand";

import type { ImageRound, Step, StoredImage } from "@/features/creator/types";

type CreatorState = {
  step: Step;
  prompt: string;
  /** Every batch of generated images, oldest first. */
  rounds: ImageRound[];
  /** The image the 3D model is built from (generated or uploaded). */
  baseImage: StoredImage | null;
  modelId: string | null;
  /** USD spent since the page was opened (sum of the costs Runware reports per call). */
  sessionSpend: number;

  setStep: (step: Step) => void;
  setPrompt: (prompt: string) => void;
  addRound: (round: ImageRound) => void;
  startModel: (modelId: string, image: StoredImage) => void;
  addSpend: (value: number | null) => void;
  reset: () => void;
};

const initialState = {
  step: "create" as Step,
  prompt: "",
  rounds: [],
  baseImage: null,
  modelId: null,
  sessionSpend: 0,
};

export const useCreatorStore = create<CreatorState>()((set) => ({
  ...initialState,

  setStep: (step) => set({ step }),
  setPrompt: (prompt) => set({ prompt }),
  addRound: (round) => set((state) => ({ rounds: [...state.rounds, round] })),
  startModel: (modelId, baseImage) => set({ modelId, baseImage, step: "model" }),
  addSpend: (value) => {
    if (!value) return;
    set((state) => ({ sessionSpend: state.sessionSpend + value }));
  },
  // Spend survives a restart: it tracks the whole testing session.
  reset: () => set((state) => ({ ...initialState, sessionSpend: state.sessionSpend })),
}));
