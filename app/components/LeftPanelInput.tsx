import { useState, useRef } from "react";
import { Upload, ClipboardPaste } from "lucide-react";
import { API_CONFIG } from '../config';

export default function LeftPanelInput({
  onUploadComplete,
  embedAndUploadToPinecone,
  onSummaryGenerated, // ✅ new prop
}: {
  onUploadComplete: (fileName: string, text: string) => void;
  embedAndUploadToPinecone: (text: string, namespace: string) => void;
  onSummaryGenerated?: (summary: string[]) => void; // ✅ optional
}) {
  const [textInput, setTextInput] = useState("");
  const [error, setError] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);

  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleFileSelect = (file: File | null) => {
    if (!file) return;
    const ext = file.name.slice(file.name.lastIndexOf(".")).toLowerCase();
    const allowed = [".pdf", ".docx"];
    if (!allowed.includes(ext)) {
      setError("Only PDF and DOCX files are supported.");
      return;
    }
    if (file.size > 25 * 1024 * 1024) {
      setError("File is too large. Max 25MB.");
      return;
    }    
    setSelectedFile(file);
    setError("");
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    handleFileSelect(file);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    handleFileSelect(file);
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleChooseClick = () => {
    fileInputRef.current?.click();
  };

  const generateSummary = async (text: string) => {
    try {
      const res = await fetch(`${API_CONFIG.ANALYZER_API}${API_CONFIG.ENDPOINTS.SUMMARY}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ docText: text }),
      });
      const json = await res.json();
      if (Array.isArray(json.summary) && onSummaryGenerated) {
        onSummaryGenerated(json.summary);
      }
    } catch (err) {
      console.error("Summary generation failed", err);
    }
  };
  
  

  const handleFileUpload = async () => {
    if (!selectedFile) return;
    const formData = new FormData();
    formData.append("file", selectedFile);
    setIsUploading(true);
    try {
      const response = await fetch(`${API_CONFIG.FLASK_APP}${API_CONFIG.ENDPOINTS.UPLOAD}`, {
        method: "POST",
        body: formData,
      });
      if (!response.ok) {
        const errData = await response.json();
        setError(errData.error || "Upload failed.");
        return;
      }      
      const data = await response.json();
      onUploadComplete(data.name, data.text);
      embedAndUploadToPinecone(data.text, data.name);
      await generateSummary(data.text); // ✅ summarize
      setSelectedFile(null);
      fileInputRef.current!.value = "";
      setTextInput("");
      setError("");
    } catch (err: any) {
      console.error("Upload error:", err);
      setError(err.message || "Upload failed.");
    } finally {
      setIsUploading(false);
    }
  };

  const handlePaste = async () => {
    if (!textInput.trim()) {
      setError("Please paste some text before submitting.");
      return;
    }
    onUploadComplete("Pasted Text", textInput);
    embedAndUploadToPinecone(textInput, "pasted-text");
    await generateSummary(textInput); // ✅ summarize
    setError("");
  };

  return (
    <div className="space-y-6">
      {/* Upload Section */}
      <div className="p-4 border rounded-xl bg-white shadow-sm space-y-4">
      <div className="flex items-center gap-2 text-gray-700 font-medium">
        <Upload size={18} />
        <span>Upload PDF or DOCX</span>
      </div>

      <p className="text-xs text-gray-500 mt-1">
        ⚠️ Only English-language documents are supported.
      </p>

        <input
          type="file"
          accept=".pdf,.docx"
          ref={fileInputRef}
          onChange={handleFileInputChange}
          className="hidden"
        />

        <div
          onClick={handleChooseClick}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          className={`border-2 border-dashed rounded-lg px-4 py-10 text-center text-sm cursor-pointer transition-all
            ${
              isDragging
                ? "border-blue-500 bg-blue-50 text-blue-700"
                : "border-gray-300 text-gray-500 hover:bg-zinc-50"
            }`}
        >
          {selectedFile ? (
            <div>
              <p className="text-gray-700">
                Selected: <strong>{selectedFile.name}</strong>
              </p>
            </div>
          ) : (
            <p>
              Drag and drop a file here, or <span className="underline">click to browse</span>
            </p>
          )}
        </div>

        <button
          onClick={handleFileUpload}
          disabled={!selectedFile || isUploading}
          className={`w-full px-4 py-2 text-sm rounded transition-colors flex items-center justify-center gap-2 ${
            isUploading
              ? "bg-blue-200 text-blue-800 cursor-wait"
              : "bg-blue-500 text-white hover:bg-blue-600"
          } disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          {isUploading ? (
            <>
              <span>Processing</span>
              <span className="flex space-x-1">
                <span className="w-1.5 h-1.5 bg-blue-800 rounded-full animate-bounce"></span>
                <span className="w-1.5 h-1.5 bg-blue-800 rounded-full animate-bounce [animation-delay:0.2s]"></span>
                <span className="w-1.5 h-1.5 bg-blue-800 rounded-full animate-bounce [animation-delay:0.4s]"></span>
              </span>
            </>
          ) : (
            "Submit File"
          )}
        </button>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}
    </div>
  );
}
