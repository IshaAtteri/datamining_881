"use client";

type ToggleParams = {
  selected: string;
  onChange: (method: string) => void;
};

const methods = [
  { id: "algo", label: "Algorithm" },
  { id: "model", label: "Model" },
];

export default function Toggle({selected, onChange,}: ToggleParams) {
  return (
    <div className="flex gap-3 justify-center mt-4">
      {methods.map((algo) => (<button key={algo.id} onClick={() => onChange(algo.id)} className={`px-4 py-2 rounded-md border transition
            ${selected === algo.id ? "bg-blue-500 text-white" : "bg-gray-100 hover:bg-gray-200"}`}> {algo.label}
        </button>
      ))}
    </div>
  );
}