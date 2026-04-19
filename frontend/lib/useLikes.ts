"use client";

import { createContext, useContext } from "react";

const MAX_LIKES = 6;
const STORAGE_KEY = "liked_slugs";

export type LikesContextType = {
  likedSlugs: string[];
  toggleLike: (slug: string) => void;
  clearLikes: () => void;
  isLiked: (slug: string) => boolean;
  isMaxLikes: boolean;
};

export const LikesContext = createContext<LikesContextType | undefined>(undefined);

export const MAX_LIKES_CONSTANT = MAX_LIKES;
export const STORAGE_KEY_CONSTANT = STORAGE_KEY;

export function useLikes() {
  const context = useContext(LikesContext);
  if (context === undefined) {
    throw new Error("useLikes must be used within a LikesProvider");
  }
  return context;
}
