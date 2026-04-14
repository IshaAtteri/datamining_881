"use client";
import {LuExpand, LuMinimize2} from "react-icons/lu";

type ExpandParams = {
  onClick: () => void;
  isOpen: boolean;
};

export default function ExpandMovie({ onClick, isOpen }: ExpandParams) {
  return (
    <button
      onClick={onClick}
      className="w-9 h-9 flex items-center justify-center rounded-full bg-black/60 hover:bg-black/80 transition hover:cursor-pointer"
    >
      {isOpen ? (
        <LuMinimize2 className="w-5 h-5 text-white" />
      ) : (
        <LuExpand className="w-5 h-5 text-white" />
      )}
    </button>
  );
}