import React from 'react';

export default function TailwindTest() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-b from-blue-900 to-black p-4">
      <div className="w-full max-w-md rounded-xl bg-white/10 p-8 backdrop-blur-lg">
        <h1 className="mb-4 text-3xl font-bold text-white">Tailwind CSS Test</h1>
        <p className="text-lg text-gray-300">
          If you can see this card with blue gradient background, Tailwind CSS is working!
        </p>
        <div className="mt-6 grid grid-cols-2 gap-4">
          <button className="rounded-lg bg-blue-500 px-4 py-2 font-medium text-white hover:bg-blue-600">
            Blue Button
          </button>
          <button className="rounded-lg bg-purple-500 px-4 py-2 font-medium text-white hover:bg-purple-600">
            Purple Button
          </button>
        </div>
      </div>
    </div>
  );
} 