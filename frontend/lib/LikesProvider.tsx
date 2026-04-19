"use client";

import { useState, useEffect, useCallback, ReactNode } from "react";
import { LikesContext, MAX_LIKES_CONSTANT, STORAGE_KEY_CONSTANT } from "./useLikes";

function getLikesFromStorage(): string[] {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY_CONSTANT) || "[]");
  } catch {
    return [];
  }
}

export function LikesProvider({ children }: { children: ReactNode }) {
  const [likedSlugs, setLikedSlugs] = useState<string[]>([]);

  useEffect(() => {
    setLikedSlugs(getLikesFromStorage());
  }, []);

  useEffect(() => {
    const handleStorageChange = () => {
      setLikedSlugs(getLikesFromStorage());
    };

    window.addEventListener("storage", handleStorageChange);
    return () => window.removeEventListener("storage", handleStorageChange);
  }, []);

  const isLiked = useCallback((slug: string) => likedSlugs.includes(slug), [likedSlugs]);

  const toggleLike = useCallback((slug: string) => {
    const currentSlugs = getLikesFromStorage();
    let newSlugs: string[];

    if (currentSlugs.includes(slug)) {
      newSlugs = currentSlugs.filter((s: string) => s !== slug);
    } else if (currentSlugs.length < MAX_LIKES_CONSTANT) {
      newSlugs = [...currentSlugs, slug];
    } else {
      return;
    }

    localStorage.setItem(STORAGE_KEY_CONSTANT, JSON.stringify(newSlugs));
    setLikedSlugs(newSlugs);
  }, []);

  const clearLikes = useCallback(() => {
    localStorage.setItem(STORAGE_KEY_CONSTANT, JSON.stringify([]));
    setLikedSlugs([]);
  }, []);

  const isMaxLikes = likedSlugs.length >= MAX_LIKES_CONSTANT;

  return (
    <LikesContext.Provider value={{ likedSlugs, toggleLike, clearLikes, isLiked, isMaxLikes }}>
      {children}
    </LikesContext.Provider>
  );
}
