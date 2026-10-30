"use client";

import { create } from "zustand";

import type { CostEntry, ImageRound, Step, StoredImage } from "@/features/creator/types";

type CreatorState = {
  step: Step;
  prompt: string;
  /** Every batch of generated images, oldest first. */
  rounds: ImageRound[];
  /** The image the 3D model is built from (generated or uploaded). */
  baseImage: StoredImage | null;
  modelId: string | null;
  costs: CostEntry[];

  setStep: (step: Step) => void;
  setPrompt: (prompt: string) => void;
  addRound: (round: ImageRound) => void;
  startModel: (modelId: string, image: StoredImage) => void;
  addCost: (label: string, value: number | null) => void;
  reset: () => void;
};

const initialState = {
  step: "create" as Step,
  prompt: "",
  rounds: [],
  baseImage: null,
  modelId: null,
  costs: [],
};

export const useCreatorStore = create<CreatorState>()((set) => ({
  ...initialState,

  setStep: (step) => set({ step }),
  setPrompt: (prompt) => set({ prompt }),
  addRound: (round) => set((state) => ({ rounds: [...state.rounds, round] })),
  startModel: (modelId, baseImage) => set({ modelId, baseImage, step: "model" }),
  addCost: (label, value) => {
    if (value === null || value === undefined) return;
    set((state) => ({ costs: [...state.costs, { label, value }] }));
  },
  // Costs survive a restart: they track the whole testing session.
  reset: () => set((state) => ({ ...initialState, costs: state.costs })),
}));
