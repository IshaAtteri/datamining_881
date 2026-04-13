"use client";

import { useState } from "react";
import { FaChevronDown } from "react-icons/fa";

type Method = "algo" | "model";

type ToggleParams = {
  selected: Method;
  onChange: (method: Method) => void;
};

const methods: {id: Method; label: string}[] = [
  { id: "algo", label: "Algorithm" },
  { id: "model", label: "Model" },
];

export default function Toggle({selected, onChange}: ToggleParams) {
  const [open, setOpen] = useState(false);

  const current = methods.find((m) => m.id === selected);

  return (
    <div className="relative inline-block mt-0.5">
      <button onClick={() => setOpen(!open)} className="flex items-center gap-2 px-3 py-1 rounded-md bg-box border hover:bg-gray-200 transition text-xs">
        {current?.label}
        <FaChevronDown className={`transition-transform duration-200 text-xs ${open ? "rotate-180" : ""}`}/>
      </button>

      {open && (<div className="absolute mt-2 w-full rounded-md border bg-white shadow-md z-50 text-xs">
        {methods.map((m) => (
          <button key={m.id} onClick={() => {onChange(m.id); setOpen(false);}}
            className={`block w-full text-left px-4 py-2 transition ${selected === m.id ? "bg-highlight/80 font-bold": "hover:bg-gray-100"}`}>
              {m.label}
          </button>
        ))}
        </div>
      )}
    </div>
  );
}