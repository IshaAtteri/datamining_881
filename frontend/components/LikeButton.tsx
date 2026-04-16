"use client";

import {IoMdHeart, IoMdHeartEmpty} from "react-icons/io";
import {useLikes} from "../lib/useLikes";

type LikeButtonProps = {
  slug: string;
};

export default function LikeButton({slug}: LikeButtonProps) {
  const {isLiked, toggleLike, isMaxLikes} = useLikes();
  const liked = isLiked(slug);
  const canLike = !liked && isMaxLikes;

  return (
    <button
      onClick={() => toggleLike(slug)}
      title={canLike ? "Like limit reached. Unlike another movie to like this one." : ""}
      className={`w-9 h-9 flex items-center justify-center rounded-full transition hover:cursor-pointer ${
        canLike
          ? "bg-gray-600/80 opacity-50 cursor-not-allowed hover:bg-gray-600/80"
          : "bg-black/60 hover:bg-black/80"
      }`}
    >
      {liked ? (
        <IoMdHeart className="w-5 h-5 text-red-500 scale-110 transition-transform" />
      ) : (
        <IoMdHeartEmpty className="w-5 h-5 text-white scale-110 transition-transform" />
      )}
    </button>
  );
}