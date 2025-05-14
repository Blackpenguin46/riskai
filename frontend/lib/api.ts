export const queryRAG = async (question: string) => {
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ question }),
  });

  if (!res.ok) {
    throw new Error(`API error: ${res.statusText}`);
  }

  return res.json();
};