import { useState } from 'react';
import { Button } from "./components/ui/button"
import { Input } from "./components/ui/input"
import { Textarea } from "./components/ui/textarea"
import { Card } from "./components/ui/card"
import { Alert, AlertDescription } from "./components/ui/alert"

const API_URL = process.env.REACT_APP_API_URL || 'https://user:1af398ff821e1117fae1faf845cd9835@local-ai-app-tunnel-w4pvbsu9.devinapps.com';
const MAX_FILE_SIZE = 1024 * 1024 * 1024; // 1GB

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [code, setCode] = useState('');
  const [description, setDescription] = useState('');
  const [directory, setDirectory] = useState('');
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }
    
    if (file.size > MAX_FILE_SIZE) {
      setError('File too large (max: 1GB)');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_URL}/api/documents`, {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      setResult(data);
      setError(null);
    } catch (err) {
      setError('Error uploading file');
      console.error(err);
    }
  };

  const handleAnalyze = async () => {
    if (!code) {
      setError('Please enter code to analyze');
      return;
    }

    try {
      const response = await fetch(`${API_URL}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code }),
      });
      const data = await response.json();
      setResult(data);
      setError(null);
    } catch (err) {
      setError('Error analyzing code');
      console.error(err);
    }
  };

  const handleGenerate = async () => {
    if (!description) {
      setError('Please enter a description');
      return;
    }

    try {
      const response = await fetch(`${API_URL}/api/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description }),
      });
      const data = await response.json();
      setResult(data);
      setError(null);
    } catch (err) {
      setError('Error generating code');
      console.error(err);
    }
  };

  const handleTrain = async () => {
    if (!directory) {
      setError('Please enter a directory path');
      return;
    }

    try {
      const response = await fetch(`${API_URL}/api/train`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ directory }),
      });
      const data = await response.json();
      setResult(data);
      setError(null);
    } catch (err) {
      setError('Error training system');
      console.error(err);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Pronto 4GL Assistant</h1>

      {error && (
        <Alert variant="destructive" className="mb-4">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="grid gap-8">
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Upload Document</h2>
          <div className="space-y-4">
            <Input
              type="file"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              accept=".4gl,.txt,.md"
            />
            <Button onClick={handleUpload}>Upload</Button>
          </div>
        </Card>

        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Analyze Code</h2>
          <div className="space-y-4">
            <Textarea
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="Enter Pronto 4GL code here..."
              className="min-h-[200px]"
            />
            <Button onClick={handleAnalyze}>Analyze</Button>
          </div>
        </Card>

        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Generate Code</h2>
          <div className="space-y-4">
            <Textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe what you want the code to do..."
              className="min-h-[200px]"
            />
            <Button onClick={handleGenerate}>Generate</Button>
          </div>
        </Card>

        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Train System</h2>
          <div className="space-y-4">
            <Input
              type="text"
              value={directory}
              onChange={(e) => setDirectory(e.target.value)}
              placeholder="Enter path to code directory..."
            />
            <Button onClick={handleTrain}>Train</Button>
          </div>
        </Card>

        {result && (
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Results</h2>
            <pre className="bg-gray-100 p-4 rounded overflow-auto">
              {JSON.stringify(result, null, 2)}
            </pre>
          </Card>
        )}
      </div>
    </div>
  );
}

export default App;
