import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const backendRes = await fetch('http://localhost:8000/query', { // This endpoint seems incorrect based on our backend, should be /submit-answers or /initialize-assessment
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req.body),
    });
    const data = await backendRes.json();
    res.status(backendRes.status).json(data);
  } catch (err) { // Changed 'error' to 'err' to match usage
    console.error("Error connecting to backend:", err); // Added console log for debugging
    res.status(500).json({ error: 'Failed to connect to backend service.' });
  }
} 