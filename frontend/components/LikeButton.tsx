"use client";

import {useState} from "react";
import {IoMdHeart, IoMdHeartEmpty} from "react-icons/io";

export default function LikeButton() {
  const [like, setLike] = useState(false);

  return (
    <button onClick={() => setLike(!like)} className="w-9 h-9 flex items-center justify-center rounded-full bg-black/60 hover:bg-black/80 transition hover:cursor-pointer">
      {like ? (<IoMdHeart className="w-5 h-5 text-red-500 scale-110 transition-transform"/>) : (<IoMdHeartEmpty className="w-5 h-5 text-white scale-110 transition-transform"/>)}
    </button>
  );
}